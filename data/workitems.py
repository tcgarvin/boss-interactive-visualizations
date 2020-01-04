from dataclasses import dataclass
from datetime import date, timedelta
import json
from math import ceil, floor
from random import choice, sample, uniform
from typing import List, TextIO

VERBS = [
    "Calibrate",
    "Hoist",
    "Rejigger",
    "Update",
    "Upgrade",
    "Implement",
    "Reimplement",
    "Find",
    "Debug",
    "Refactor",
    "Enable",
    "Disable",
    "Fix",
    "Deploy",
    "Engineer",
    "Create",
    "Manage",
    "Retest",
    "Reverse-engineer",
    "Make",
    "Address",
    "Backup",
    "Restore",
]

NOUNS = [
    "Gargleblaster",
    "Cache",
    "Postgres Backend",
    "Feature Flag for A",
    "Feature Flag for B",
    "Database Schema",
    "Easter Egg",
    "Meme Generator",
    "Autocomplete",
    "AI",
    "Machine Learning",
    "Blockchain",
    "Wormhole",
    "Hyperdrive",
    "Oracle",
    "Kafka Backend",
    "Mongo Backend",
    "Neo4j Backend",
    "S3 Connector",
    "Quantum Speedup",
    "Voice Assistant",
    "Azure Configuration",
    "GCP Configuration",
    "React Frontend",
    "Vue Frontend",
    "jQuery Frontend",
    "CLI Frontend",
    "gRPC Interface",
    "REST Interface",
    "User Profiles",
    "Default Configuration",
    "Secret Store",
    "Kubernetes Cluster",
    "Intern Project",
]

POINTS = [1,2,3,5,8,13,21]

@dataclass
class WorkItem:
    name: str
    points: int
    points_remaining: float
    iteration_start: date = None
    start_work: date = None
    finish: date = None
    owner: str = None
    iteration_action = 0

@dataclass
class TeamMember:
    name: str
    improvement_factor: float
    consistency_factor: float
    average_points: float
    working_on: WorkItem = None

workitem_number = 0
def pull_backlog_item() -> WorkItem:
    global workitem_number
    workitem_number += 1
    number = workitem_number
    name = f"{choice(VERBS)} the {choice(NOUNS)}"
    points = choice(POINTS)
    return WorkItem(name, points, points)

def log(d, message):
    print(f"{d.isoformat()}: {message}")

def generate_workitems(team_members : List[TeamMember]) -> List[WorkItem]:
    workitems = []
    iteration_start = date(2019, 7, 8)
    week = timedelta(7)

    in_progress_items = []
    i = 0
    while iteration_start.month < 12:
        i += 1
        iteration = f"Iteration {i}"
        new_iteration_items = []

        log(iteration_start, f"Generating {iteration}")
        
        point_target = sum(member.average_points for member in team_members)
        points_targeted = sum(floor(item.points_remaining) for item in in_progress_items)
        while points_targeted < point_target:
            next_workitem = pull_backlog_item()
            next_workitem.iteration_start = iteration_start
            points_targeted += next_workitem.points
            new_iteration_items.append(next_workitem)
            workitems.append(next_workitem)
            log(iteration_start, f"Added '{next_workitem.name}' to {iteration}")

        for member in team_members:
            c = member.consistency_factor
            member.iteration_action = member.average_points * (1 + uniform(-c, c))

        for d in range(5):
            today = iteration_start + timedelta(d)

            for member in sample(team_members, len(team_members)):
                daily_points = member.iteration_action / 5
                while daily_points > 0:
                    if member.working_on is None and len(new_iteration_items) == 0:
                        break

                    if member.working_on is None:
                        member.working_on = new_iteration_items.pop()
                        in_progress_items.append(member.working_on)
                        member.working_on.start_work = today
                        member.working_on.owner = member.name
                        log(today, f"{member.name} picked up '{member.working_on.name}'")

                    if daily_points >= member.working_on.points_remaining:
                        log(today, f"{member.name} finished '{member.working_on.name}'")
                        daily_points -= member.working_on.points_remaining
                        member.working_on.points_remaining = 0
                        member.working_on.finish = today
                        in_progress_items.remove(member.working_on)
                        member.working_on = None
                    else:
                        member.working_on.points_remaining -= daily_points
                        daily_points = 0

        for member in team_members:
            member.consistency_factor *= (1 - member.improvement_factor / 2)
            member.average_points *= (1 + member.improvement_factor)

        iteration_start = iteration_start + week

    return workitems

if __name__ == "__main__":
    import sys

    team_members = []
    team_members.append(TeamMember(
        "Eli",
        0.1,
        0.6,
        4.25
        
    ))

    team_members.append(TeamMember(
        "Rachel",
        0.05,
        0.4,
        6
    ))

    team_members.append(TeamMember(
        "Kensie",
        0,
        0.3,
        13
    ))

    team_members.append(TeamMember(
        "Heather",
        0,
        0.5,
        13
    ))

    team_members.append(TeamMember(
        "Sam",
        -0.02,
        0.4,
        7
    ))

    workitems = generate_workitems(team_members)

    workitems_json = []
    for workitem in workitems:
        start = workitem.iteration_start.isoformat() if workitem.iteration_start is not None else None
        start_work = workitem.start_work.isoformat() if workitem.start_work is not None else None
        end = workitem.finish.isoformat() if workitem.finish is not None else None
        workitems_json.append({
            "name": workitem.name,
            "points": workitem.points,
            "owner": workitem.owner,
            "iterationStartDate": start,
            "workStartDate": start_work,
            "finishDate": end
        })

    with open("workitems.json", "w") as output_file:
        json.dump(workitems_json, output_file)
