import json
import os
import hashlib
from pathlib import Path

import numpy as np
import qiskit

from qiskit import QuantumCircuit, transpile, Aer, IBMQ
from qiskit.aqua.utils import tensorproduct
from qiskit.providers import provider
from qiskit.tools import job_monitor

IBMQ.save_account(
    '280beccbee94456a161a6cbc217e1366bc278bf60e22bd30281fa0ca5bec6e50897278ef818f3c53f6700e04b9ed32ea364195044413b7e02836a79d886b03d9',
    overwrite=True)
provider = IBMQ.get_provider(hub='ibm-q-research')


def __save_job(job_id, circuit, system, shots, name):
    new_name = name
    job_old = {}
    if os.path.isfile("jobs.json"):
        with open("jobs.json", "r") as read_file:
            job_old = json.load(read_file)
            new_name = ""
            for key in job_old.keys():
                if key == name:
                    if job_id == job_old[key].split('|')[0]:
                        return
                    new_name = set_name(job_old, name)
                    break
            if new_name == "":
                new_name = name
    with open("jobs.json", "w") as write_file:
        job = {new_name: job_id + "|" + circuit + "|" + system + "|" + str(shots)}
        job_old.update(job)
        json.dump(job_old, write_file, indent=4)


def save_job(job, name):
    system = job.backend().name()
    shots = job.backend_options().get("shots")
    job_id = job.job_id()
    circuits = job.circuits()
    hash_cir = ""
    for cir in circuits:
        hash_cir = hash_cir + cir.qasm()

    hash_cir = str(hashlib.md5(hash_cir.encode()).hexdigest())
    __save_job(job_id, hash_cir, system, shots, name)


def set_name(job, name, i=0):
    for key in job.keys():
        if key == name + str(i):
            j = i + 1
            return set_name(job, name, j)

    return name + str(i)


def execute(circuit, system, name, shots=8000, override=False):
    if system == 'qasm_simulator':
        qcomp = Aer.get_backend(system)
        exp = qiskit.execute(circuit, qcomp, shots=shots)
        return exp

    qcomp = provider.get_backend(system)
    circuit_name = ""
    if isinstance(circuit, QuantumCircuit):
        circuit_name = circuit.qasm()
    else:
        for cir in circuit:
            circuit_name = circuit_name + cir.qasm()
    circuit_name = str(hashlib.md5(circuit_name.encode()).hexdigest())

    if os.path.isfile("jobs.json") and not override:
        with open("jobs.json", "r") as read_file:
            job = json.load(read_file)
        for details in job.values():
            params = details.split('|')

            if params[1] == circuit_name and params[2] == system and params[3] == str(shots):
                print("Retrieved from memory")
                __save_job(params[0], circuit_name, system, shots, name)
                return qcomp.retrieve_job(params[0])

    exp = qiskit.execute(circuit, qcomp, shots=shots)
    job_monitor(exp)
    __save_job(exp.job_id(), circuit_name, system, shots, name)
    return exp


def retrieve(name):
    if os.path.isfile("jobs.json"):
        with open("jobs.json", "r") as read_file:
            job_dic = json.load(read_file)
        details = job_dic.get(name, False)
        if not details:
            raise NameError('No such experiment')
        system = details.split('|')[2]
        qcomp = provider.get_backend(system)
        print("Retrieved from memory")
        return qcomp.retrieve_job(details.split('|')[0])
