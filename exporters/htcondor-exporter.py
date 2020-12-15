# based on https://github.com/niclabs/htcondor-monitor implementation

import argparse
import time

import htcondor
import re

from prometheus_client import start_wsgi_server
from prometheus_client import REGISTRY, make_wsgi_app
from prometheus_client.core import GaugeMetricFamily
from wsgiref.simple_server import make_server


class JobRunningTimeMetric:
    ''' class defining a metric contaning job running time '''
    def __init__(self):
        self.time = GaugeMetricFamily('condor_job_avg_running_time_seconds',
                                      'Average running time for completed jobs for the specific cluster and submitter',
                                      labels=['submitter', 'cluster', 'id'])

    def as_list(self):
        return [self.time]

class JobStateMetric:
    ''' class defining a metric contaning job state (idle/running/held/completed) '''
    def __init__(self):
        self.idle = GaugeMetricFamily('condor_job_state_idle',
                                      'Number of jobs on the idle state for a given cluster and submitter',
                                      labels=['submitter', 'cluster', 'id'])
        self.running = GaugeMetricFamily('condor_job_state_running',
                                         'Number of jobs on the running state for a given cluster and submitter',
                                         labels=['submitter', 'cluster', 'id'])
        self.held = GaugeMetricFamily('condor_job_state_held',
                                      'Number of jobs on the held state for a given cluster and submitter',
                                      labels=['submitter', 'cluster', 'id'])

        self.completed = GaugeMetricFamily('condor_job_state_completed',
                                           'Number of jobs on the completed state for a given cluster and submitter',
                                           labels=['submitter', 'cluster', 'id'])

    def as_list(self):
        return [self.idle, self.running, self.held, self.completed]


class SlotActivityMetric:
    ''' class defining a metric contaning Slot activity (idle/busy)'''
    def __init__(self):
        self.idle = GaugeMetricFamily('condor_slot_activity_idle',
                                      'Is this slot idle', labels=['machine', 'slot', 'address'])
        self.busy = GaugeMetricFamily('condor_slot_activity_busy',
                                      'Is this slot busy', labels=['machine', 'slot', 'address'])

    def as_list(self):
        return [self.idle, self.busy]

class SlotStateMetric:
    ''' class defining a metric contaning Slot state (owner/claimed/unclaimed)'''
    def __init__(self):
        self.owner = GaugeMetricFamily('condor_slot_state_owner',
                                       'Is this slot in the owner state', labels=['machine', 'slot', 'address'])
        self.claimed = GaugeMetricFamily('condor_slot_state_claimed',
                                         'Is this slot in the claimed state', labels=['machine', 'slot', 'address'])
        self.unclaimed = GaugeMetricFamily('condor_slot_state_unclaimed',
                                           'Is this slot in the unclaimed state', labels=['machine', 'slot', 'address'])

    def as_list(self):
        return [self.owner, self.claimed, self.unclaimed]




class CondorJobCluster:
    ''' class defining a cluster of jobs '''

    def __init__(self, cluster_id, submitter):
        self.cluster_id = cluster_id
        self.submitter = submitter
        self.jobs = {}

    def global_id(self):
        return "%d@%s" % (self.cluster_id, self.submitter)

    def is_active(self):
        ''' if all jobs in the cluster are completed, the cluster of jobs is inactive, otherwise is active '''
        for job in iter(self.jobs.values()):
            if job.state != "Completed":
                return True
        return False

    def update_job_state(self, state_metric):
        ''' loop across all jobs in the cluster counting how many jobs are in each possible state (idle/held/running/completed) and update accordingly a state_metric'''
        count_held = 0
        count_idle = 0
        count_running = 0
        count_completed = 0
        for job in iter(self.jobs.values()):
            if job.state == "Running":
                count_running += 1
            elif job.state == "Idle":
                count_idle += 1
            elif job.state == "Held":
                count_held += 1
            elif job.state == "Completed":
                count_completed += 1

        state_metric.idle.add_metric([self.submitter, str(self.cluster_id), self.global_id()], count_idle)
        state_metric.held.add_metric([self.submitter, str(self.cluster_id), self.global_id()], count_held)
        state_metric.running.add_metric([self.submitter, str(self.cluster_id), self.global_id()], count_running)
        state_metric.completed.add_metric([self.submitter, str(self.cluster_id), self.global_id()], count_completed)

    def update_job_running_time(self, runtime_metric):
        ''' loop across all jobs in the cluster getting the mean runtime value of completed jobs in the clusyer and update accordingly a runtime_metric'''
        runtime_sum = 0.0
        runtime_count = 0.0
        for job in iter(self.jobs.values()):
            if job.state == "Completed":
                runtime_sum += job.running_time
                runtime_count += 1
        if runtime_count == 0:
            runtime_avg = 0
        else:
            runtime_avg = runtime_sum / runtime_count
        runtime_metric.time.add_metric([self.submitter, str(self.cluster_id), self.global_id()], runtime_avg)

class Machine:
    ''' class defining a machine '''

    def __init__(self, name, address):
        self.name = name
        self.address = address
        self.slots = {}

    def reset_slots_metrics(self):
        for slot in iter(self.slots.values()):
            slot.reset_metrics()

    def update_activity(self, activity_metric):
        ''' loop across all slots in the machine getting their activity (busy/idle) and update accordingly an activity_metric'''
        for slot in iter(self.slots.values()):
            is_busy = slot.activity == "Busy"
            is_idle = slot.activity == "Idle"
            activity_metric.busy.add_metric([self.name, str(slot.slot_id), self.address], is_busy)
            activity_metric.idle.add_metric([self.name, str(slot.slot_id), self.address], is_idle)

    def update_state(self, state_metric):
        ''' loop across all slots in the machine getting their state (owner/claimed/unclaimed) and update accordingly a state_metric'''
        for slot in iter(self.slots.values()):
            is_owner = slot.state == "Owner"
            is_claimed = slot.state == "Claimed"
            is_unclaimed = slot.state == "Unclaimed"
            state_metric.owner.add_metric([self.name, str(slot.slot_id), self.address], is_owner)
            state_metric.claimed.add_metric([self.name, str(slot.slot_id), self.address], is_claimed)
            state_metric.unclaimed.add_metric([self.name, str(slot.slot_id), self.address], is_unclaimed)


class Slot:
    ''' class defining a slot '''
    def __init__(self, slot_id):
        self.slot_id = slot_id
        self.activity = None
        self.state = None

    def reset_metrics(self):
        self.activity = None
        self.state = None

class CondorJob:
    ''' class defining a job '''
    def __init__(self, job_id):
        self.job_id = job_id
        self.state = None
        self.execute_machine = None
        self.running_time = 0

    def reset_state(self):
        self.state = None

def parse_address(address):
    regex_match = re.compile(r'<(\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3}):.*').match(address)
    if regex_match is not None:
        return regex_match.group(1)
    return ""


def parse_submitter(user):
    # User is a string in the form "username@machine" we want only the 'machine' part
    regex_match = re.compile(r'.*@(.*)$').match(user)
    if regex_match is not None:
        return regex_match.group(1)
    return ""


def get_cluster_history(schedd, cluster):
    '''
    get jobs from condor_history with the same cluster id as the "cluster object": 
    if any of the obtained jobs is not in that "cluster object", 
    it is added to the "cluster object" with status and runtime info
    ''' 

    requirements = 'Machine =?= %s && ClusterId == %d' % (cluster.submitter, cluster.cluster_id)
    projection = ["Owner", "ExitStatus", "ProcId", "JobStatus", "RemoteSlotID", "RemoteHost", "RemoteWallClockTime"]
    jobs = schedd.history(requirements, projection)
    for job in jobs:
        job_id = job.get("ProcId", -1)
        status = job.get("JobStatus", "")
        runtime = job.get("RemoteWallClockTime", 0)
        if job not in cluster.jobs:
            cluster.jobs[job_id] = CondorJob(job_id)
        current_job = cluster.jobs[job_id]
        current_job.state = parse_job_status(status)
        current_job.running_time = runtime


def parse_job_status(status_code):
    if status_code == 1:
        return "Idle"
    elif status_code == 2:
        return "Running"
    elif status_code == 5:
        return "Held"
    elif status_code == 4:
        return "Completed"
    return ""


class CondorCollector(object):
    '''
    class defining a collector for htcondor 
    '''

    def __init__(self, pool=None):
        self.machines = {}
        self.clusters = {}
        self.inactive_clusters = []
        self.coll = htcondor.Collector(pool)

    def query_all_slots(self, projection=[]):
        ''' get all Startd Ads '''
        all_submitters_query = self.coll.query(htcondor.AdTypes.Startd, projection=projection)
        return all_submitters_query

    def get_all_submitters(self):
        '''get all Submitters'''

        projection = ["Name", "MyAddress"]
        all_submitters_query = self.coll.query(htcondor.AdTypes.Submitter, projection=projection)
        schedds = []
        for submitter in all_submitters_query:
            schedds.append(htcondor.Schedd(submitter))
        return schedds

    def get_machine_list(self): 
        return [machine for machine in iter(self.machines.values())]

    def query_all_machines(self):
        ''' 
        1) get all slots, aggregating them into machines, and return machines list
        2) remove killed wns from list
        '''

        projection = ["Machine", "State", "Name", "SlotID", "Activity", "MyAddress"]
        slots_info = self.query_all_slots(projection=projection)
        for slot in slots_info:
            name = slot.get("Machine", None)
            slot_id = slot.get("SlotID", None)
            activity = slot.get("Activity", None)
            state = slot.get("State", None)
            address = parse_address(slot.get("MyAddress", ""))
            if name not in self.machines:
                self.machines[name] = Machine(name, address)
            current_machine = self.machines[name]
            current_machine.address = address
            if slot_id not in current_machine.slots:
                current_machine.slots[slot_id] = Slot(slot_id)
            current_slot = current_machine.slots[slot_id]
            current_slot.activity = activity
            current_slot.state = state
        
        #new######## delete killed wn
        to_delete=[]
        for key,value in self.machines.items():
            is_alive = False
            for slot in slots_info:
                if key == slot.get("Machine", None):
                    is_alive = True
            if is_alive == False:
                to_delete.append(key)
        for i in to_delete:
            del self.machines[i]
        ###############

        return self.get_machine_list()

    def collect_machine_metrics(self, activity_metrics, state_metrics):
        ''' update slots metrics with current values '''
        for machine in iter(self.machines.values()):
            machine.reset_slots_metrics()
        machines = self.query_all_machines()
        for machine in machines:
            machine.update_activity(activity_metrics)
            machine.update_state(state_metrics)

    def get_jobs_from_schedd(self, schedd):
        ''' 
        1) get all jobs from scheduler and for each job
           - if the cluster it belongs to is not in the clusters list, create a "cluster object" and add the cluster to the list;
           - if the job is not in the jobs list of the "cluster object" it belongs to, create a "job object" and add it to the list;
           - if the job is running, add execute_machine info to "job object"
        no 2) for each cluster get jobs from condor_history with the same cluster_id, if any of the obtained jobs is not in that "cluster object", it is added to the "cluster object" with status and runtime info
        3) return list of clusters        
        '''

        projection = ["Owner", "User", "ExitStatus", "Cmd", "ClusterId", "ProcId",
                      "GlobalJobId", "JobStatus", "RemoteSlotID", "RemoteHost"]
        # requirements = 'Machine =?= %s' % submitter.name
        try:
            jobs_from_submitter = schedd.xquery(projection=projection)
        except RuntimeError:
            return []
        for job in jobs_from_submitter:
            cluster_id = job.get("ClusterId", None)
            job_id = job.get("ProcId", None)
            status = job.get("JobStatus", None)
            submitter = job.get("User", "")
            if cluster_id not in self.clusters:
                self.clusters[cluster_id] = CondorJobCluster(cluster_id, parse_submitter(submitter))
            if job_id not in self.clusters[cluster_id].jobs:
                self.clusters[cluster_id].jobs[job_id] = CondorJob(job_id)
            self.clusters[cluster_id].jobs[job_id].state = parse_job_status(status)
            if self.clusters[cluster_id].jobs[job_id].state == "Running":
                self.clusters[cluster_id].jobs[job_id].execute_machine = job.get("RemoteHost", "")
        #for cluster in iter(self.clusters.values()):
        #    get_cluster_history(schedd, cluster)
        return [cluster for cluster in iter(self.clusters.values())]

    def collect_job_metrics(self, job_state_metrics, job_time_metrics):
        '''
        inactive_clusters is a list of tuples: the first is the cluster, the second is the time to live (TTL).
        no 1) loop on all clusters: for each cluster, if all jobs in the cluster are completed, (cluster, 6) is added to inactive_clusters list
        no 2) Remove inactive clusters from main list
        no 3) Decrease time to live for all inactive clusters and remove old inactive clusters
        no 4) loop on all inactive clusters: 
           - loop across all jobs in the cluster counting how many jobs are in each possible state (idle/held/running/completed) and update accordingly the job_state_metrics
           - loop across all jobs in the cluster getting the mean runtime value of completed jobs in the clusyer and update accordingly a the job_time_metrics
        5) loop on all submitters:
           - loop on all clusters from that submitter:
             - loop across all jobs in the cluster counting how many jobs are in each possible state (idle/held/running/completed) and update accordingly the job_state_metrics
             - loop across all jobs in the cluster getting the mean runtime value of completed jobs in the clusyer and update accordingly the job_time_metrics
        '''


        #for cluster in iter(self.clusters.values()):
        #    if not cluster.is_active():
        #        self.inactive_clusters.append((cluster, 6))
        #for cluster, ttl in self.inactive_clusters:
        #    if cluster.cluster_id in self.clusters:
        #        del self.clusters[cluster.cluster_id]
        #self.inactive_clusters = [(cluster, i-1) for cluster, i in self.inactive_clusters if i > 0]
        
        #for cluster, ttl in self.inactive_clusters:
        #    cluster.update_job_state(job_state_metrics)
        #    cluster.update_job_running_time(job_time_metrics)
        
        submitter_schedds = self.get_all_submitters()
        for submitter in submitter_schedds:
            for cluster in self.get_jobs_from_schedd(submitter):
                cluster.update_job_state(job_state_metrics)
                cluster.update_job_running_time(job_time_metrics)


    def collect(self):
        ''' collect everything and return metrics '''

        activity_metrics = SlotActivityMetric()
        state_metrics = SlotStateMetric()
        job_state_metrics = JobStateMetric()
        job_time_metrics = JobRunningTimeMetric()
        metrics = [activity_metrics, state_metrics, job_state_metrics, job_time_metrics]

        self.collect_machine_metrics(activity_metrics, state_metrics)
        self.collect_job_metrics(job_state_metrics, job_time_metrics)
        metrics_list = []
        for m in metrics:
            metrics_list += m.as_list()
        for m in metrics_list:
            yield m

def main():
    parser = argparse.ArgumentParser(description="Run condor exporter to expose metrics for prometheus consumption")
    parser.add_argument('-p', '--port', type=int, default=9118, required=False,
                        help='Specify a port to be used. Defaults to 9118')
    parser.add_argument('-a', '--host', type=str, default='localhost', required=False,
                        help='Host address to listen on. Defaults to localhost')
    parser.add_argument('-c', '--collector', type=str, default='', required=False,
                        help='Condor collector address. Defaults to localhost')
    args = parser.parse_args()
    port = args.port
    address = args.host
    collector_address = args.collector

    try:
        REGISTRY.register(CondorCollector(collector_address))
        app = make_wsgi_app()
        httpd = make_server('', port, app)
        httpd.serve_forever()
        print("Exporter listening on %s:%d" % (address, port))
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Interrupted, Shutting down")
        exit(0)


if __name__ == "__main__":
    main()
