"""Centralized Traffic Sign Metadata and Descriptions.

Defines the canonical 43 traffic sign classes corresponding to the
German Traffic Sign Recognition Benchmark (GTSRB) standard and aligns
with the seed reference labels.csv.
"""

from typing import Dict, Any, Optional
import os
import csv

# Canonical 43 GTSRB classes mapping class ID -> metadata
TRAFFIC_SIGN_METADATA: Dict[int, Dict[str, Any]] = {
    0: {
        "id": 0,
        "code": "speed_limit_20",
        "name": "Speed Limit (20 km/h)",
        "category": "Speed Limit / Regulatory",
        "shape": "Circular with red border and black numbers",
        "description": "Restricts the maximum allowable vehicle speed to 20 kilometers per hour.",
        "action": "Slow down to 20 km/h or below. Typically found in residential living areas, school zones, or shared pedestrian spaces."
    },
    1: {
        "id": 1,
        "code": "speed_limit_30",
        "name": "Speed Limit (30 km/h)",
        "category": "Speed Limit / Regulatory",
        "shape": "Circular with red border and black numbers",
        "description": "Restricts the maximum allowable vehicle speed to 30 kilometers per hour.",
        "action": "Maintain vehicle speed at or below 30 km/h. Standard in urban neighborhoods, school zones, and city centers."
    },
    2: {
        "id": 2,
        "code": "speed_limit_50",
        "name": "Speed Limit (50 km/h)",
        "category": "Speed Limit / Regulatory",
        "shape": "Circular with red border and black numbers",
        "description": "Restricts the maximum allowable vehicle speed to 50 kilometers per hour.",
        "action": "Drive at or below 50 km/h. This is the standard default speed limit inside built-up urban roads."
    },
    3: {
        "id": 3,
        "code": "speed_limit_60",
        "name": "Speed Limit (60 km/h)",
        "category": "Speed Limit / Regulatory",
        "shape": "Circular with red border and black numbers",
        "description": "Restricts the maximum allowable vehicle speed to 60 kilometers per hour.",
        "action": "Drive at or below 60 km/h. Typically posted on multi-lane urban arterial roads or peripheral city thoroughfares."
    },
    4: {
        "id": 4,
        "code": "speed_limit_70",
        "name": "Speed Limit (70 km/h)",
        "category": "Speed Limit / Regulatory",
        "shape": "Circular with red border and black numbers",
        "description": "Restricts the maximum allowable vehicle speed to 70 kilometers per hour.",
        "action": "Drive at or below 70 km/h. Common on semi-rural roads, transition zones between highways and towns."
    },
    5: {
        "id": 5,
        "code": "speed_limit_80",
        "name": "Speed Limit (80 km/h)",
        "category": "Speed Limit / Regulatory",
        "shape": "Circular with red border and black numbers",
        "description": "Restricts the maximum allowable vehicle speed to 80 kilometers per hour.",
        "action": "Drive at or below 80 km/h. Standard on non-urban roads, expressways with lower limits, and ring roads."
    },
    6: {
        "id": 6,
        "code": "end_speed_limit_80",
        "name": "End of Speed Limit (80 km/h)",
        "category": "De-restriction",
        "shape": "Circular white sign with diagonal grey/black slash",
        "description": "Indicates the termination of the 80 km/h speed limit zone.",
        "action": "Resume the standard statutory speed limit for the prevailing road category (e.g., standard rural speed)."
    },
    7: {
        "id": 7,
        "code": "speed_limit_100",
        "name": "Speed Limit (100 km/h)",
        "category": "Speed Limit / Regulatory",
        "shape": "Circular with red border and black numbers",
        "description": "Restricts the maximum allowable vehicle speed to 100 kilometers per hour.",
        "action": "Maintain speed at or below 100 km/h. Standard maximum limit on open single-carriageway highways."
    },
    8: {
        "id": 8,
        "code": "speed_limit_120",
        "name": "Speed Limit (120 km/h)",
        "category": "Speed Limit / Regulatory",
        "shape": "Circular with red border and black numbers",
        "description": "Restricts the maximum allowable vehicle speed to 120 kilometers per hour.",
        "action": "Maintain speed at or below 120 km/h. Frequently posted on dual-carriageways and motorways."
    },
    9: {
        "id": 9,
        "code": "no_passing_for_vehicles_over_two_wheels",
        "name": "No Passing (Overtaking Prohibited)",
        "category": "Prohibitory",
        "shape": "Circular with red border, showing a red car alongside a black car",
        "description": "Prohibits all motor vehicles from overtaking or passing other multi-track motor vehicles.",
        "action": "Stay in your lane behind the preceding vehicle. Do not overtake until an end-of-restriction sign is reached."
    },
    10: {
        "id": 10,
        "code": "no_passing_for_trucks",
        "name": "No Passing for Heavy Goods Vehicles",
        "category": "Prohibitory",
        "shape": "Circular with red border, showing a red heavy truck overtaking a black car",
        "description": "Prohibits goods vehicles with a gross permissible weight exceeding 3.5 metric tons from overtaking.",
        "action": "Heavy transport drivers must remain in the right-hand lane without passing. Passenger vehicles may pass if safe."
    },
    11: {
        "id": 11,
        "code": "priority_road_intersection",
        "name": "Right-of-Way at Next Intersection",
        "category": "Priority / Warning",
        "shape": "Triangular with red border and a bold cross symbol",
        "description": "Warns of an upcoming crossroads where traffic on this road has right-of-way over intersecting cross-traffic.",
        "action": "Proceed with caution. You have priority over traffic entering from side streets, but maintain vigilance."
    },
    12: {
        "id": 12,
        "code": "priority_road",
        "name": "Priority Road (Main Road)",
        "category": "Priority",
        "shape": "Diamond shape with yellow center and white border",
        "description": "Grants right-of-way to vehicles traveling on this road continuously at all upcoming junctions until cancelled.",
        "action": "You have priority over cross traffic at subsequent intersections until an End of Priority Road sign appears."
    },
    13: {
        "id": 13,
        "code": "give_way",
        "name": "Yield / Give Way",
        "category": "Priority / Regulatory",
        "shape": "Inverted downward triangle with red border and white center",
        "description": "Requires drivers to give way to oncoming or intersecting vehicles on the major road.",
        "action": "Slow down, yield right-of-way to all cross-traffic, and stop if necessary to allow other vehicles to proceed safely."
    },
    14: {
        "id": 14,
        "code": "stop",
        "name": "Stop Sign",
        "category": "Priority / Mandatory",
        "shape": "Octagonal red sign with white STOP lettering",
        "description": "Mandates that every approaching vehicle must come to a complete, full stop before the stop line.",
        "action": "Come to a complete standstill at the stop line or intersection. Check all directions and proceed only when clear."
    },
    15: {
        "id": 15,
        "code": "no_vehicles",
        "name": "No Vehicles in Both Directions",
        "category": "Prohibitory",
        "shape": "Circular with red border and plain white interior",
        "description": "Prohibits all vehicles (cars, motorcycles, trucks) from entering the roadway in either direction.",
        "action": "Do not enter. This road is closed to vehicular traffic (often reserved for emergency vehicles or pedestrians)."
    },
    16: {
        "id": 16,
        "code": "vehicles_over_3_5_tons_prohibited",
        "name": "Vehicles Exceeding 3.5 Tons Prohibited",
        "category": "Prohibitory",
        "shape": "Circular with red border and truck silhouette",
        "description": "Prohibits heavy goods vehicles exceeding 3.5 metric tons gross laden weight from entering.",
        "action": "Commercial heavy vehicle operators must find an alternate designated detour route. Light cars are unaffected."
    },
    17: {
        "id": 17,
        "code": "no_entry",
        "name": "No Entry (One-Way Street)",
        "category": "Prohibitory",
        "shape": "Circular red sign with a solid horizontal white bar",
        "description": "Prohibits all vehicular entry into this end of a roadway or one-way street.",
        "action": "Do not drive past this sign under any circumstances. Doing so would enter against opposing traffic."
    },
    18: {
        "id": 18,
        "code": "general_caution",
        "name": "General Caution / Hazard Ahead",
        "category": "Warning",
        "shape": "Triangular with red border and black exclamation mark",
        "description": "Warns of imminent hazards or unspecified dangers on the road ahead.",
        "action": "Reduce vehicle speed, heighten alertness, and prepare to respond to unexpected road hazards."
    },
    19: {
        "id": 19,
        "code": "dangerous_left_curve",
        "name": "Dangerous Curve to the Left",
        "category": "Warning",
        "shape": "Triangular with red border and leftward curving arrow",
        "description": "Warns of a sharp or hazardous curve to the left ahead.",
        "action": "Decelerate smoothly before entering the curve and maintain lane discipline without sudden steering inputs."
    },
    20: {
        "id": 20,
        "code": "dangerous_right_curve",
        "name": "Dangerous Curve to the Right",
        "category": "Warning",
        "shape": "Triangular with red border and rightward curving arrow",
        "description": "Warns of a sharp or hazardous curve to the right ahead.",
        "action": "Decelerate before the bend, position your vehicle properly, and stay well within your lane."
    },
    21: {
        "id": 21,
        "code": "double_curve",
        "name": "Double Curve Ahead",
        "category": "Warning",
        "shape": "Triangular with red border and winding S-curve arrow",
        "description": "Warns of two successive sharp bends in close proximity, the first being to the left or right.",
        "action": "Moderate speed and prepare for alternating directional centrifugal forces through both consecutive bends."
    },
    22: {
        "id": 22,
        "code": "bumpy_road",
        "name": "Bumpy / Uneven Road Surface",
        "category": "Warning",
        "shape": "Triangular with red border showing two raised humps",
        "description": "Warns of severe irregularities, potholes, dips, or bumps in the road surface ahead.",
        "action": "Reduce speed to prevent vehicle damage, loss of traction, or dangerous bouncing."
    },
    23: {
        "id": 23,
        "code": "slippery_road",
        "name": "Slippery Road Surface",
        "category": "Warning",
        "shape": "Triangular with red border showing a skidding vehicle",
        "description": "Warns of conditions causing reduced tire friction (wet leaves, oil, frost, or smooth asphalt).",
        "action": "Avoid sudden braking, abrupt steering, or rapid acceleration. Increase following distance."
    },
    24: {
        "id": 24,
        "code": "road_narrows_right",
        "name": "Road Narrows on the Right",
        "category": "Warning",
        "shape": "Triangular with red border showing constriction from the right",
        "description": "Warns that the roadway narrows or merges from the right side ahead.",
        "action": "Prepare to merge smoothly, observe surrounding traffic, and yield if your lane is ending."
    },
    25: {
        "id": 25,
        "code": "road_work",
        "name": "Road Work Ahead",
        "category": "Warning",
        "shape": "Triangular with red border showing a worker with a shovel",
        "description": "Warns of maintenance, construction, road crews, or machinery operating on or near the roadway.",
        "action": "Slow down, follow detour markings or temporary signals, and watch closely for workers and loose gravel."
    },
    26: {
        "id": 26,
        "code": "traffic_signals",
        "name": "Traffic Signals Ahead",
        "category": "Warning",
        "shape": "Triangular with red border showing vertical red, amber, green circles",
        "description": "Warns of an upcoming signal-controlled intersection or pedestrian signal.",
        "action": "Prepare to stop if the light changes. Useful on high-speed roads where signals might appear unexpectedly."
    },
    27: {
        "id": 27,
        "code": "pedestrians",
        "name": "Pedestrian Crossing Ahead",
        "category": "Warning",
        "shape": "Triangular with red border showing a person crossing",
        "description": "Warns of an upcoming marked zebra crossing or high pedestrian traffic area.",
        "action": "Slow down and yield right-of-way to pedestrians crossing or waiting to cross."
    },
    28: {
        "id": 28,
        "code": "children_crossing",
        "name": "Children Crossing / School Zone",
        "category": "Warning",
        "shape": "Triangular with red border showing two school children running",
        "description": "Warns of schools, kindergartens, parks, or playgrounds nearby where children may enter the road.",
        "action": "Exercise extreme caution, keep speed very low, and be prepared for children darting into traffic."
    },
    29: {
        "id": 29,
        "code": "bicycles_crossing",
        "name": "Bicycle Crossing Ahead",
        "category": "Warning",
        "shape": "Triangular with red border showing a bicycle",
        "description": "Warns that cyclists may cross or enter the roadway from an intersecting bicycle path.",
        "action": "Watch carefully for cyclists on both sides and yield where designated by local traffic regulations."
    },
    30: {
        "id": 30,
        "code": "wild_animals",
        "name": "Wild Animals Crossing / Ice Hazard",
        "category": "Warning",
        "shape": "Triangular with red border showing a jumping deer / hazard symbol",
        "description": "Warns of potential deer, game, or wild animals unexpectedly crossing forest and rural corridors.",
        "action": "Drive with vigilance during twilight and nighttime. If an animal appears, brake firmly; do not swerve recklessly."
    },
    31: {
        "id": 31,
        "code": "end_of_speed_and_passing_limits",
        "name": "End of All Speed and Passing Limits",
        "category": "De-restriction",
        "shape": "Circular white sign with multiple diagonal black stripes",
        "description": "Cancels all previous local speed limits, overtaking bans, and temporary restrictions.",
        "action": "Standard default national traffic rules apply from this point onward."
    },
    32: {
        "id": 32,
        "code": "go_straight_or_right",
        "name": "Mandatory Go Straight or Turn Right",
        "category": "Mandatory",
        "shape": "Circular blue sign with straight and right-turn arrows",
        "description": "Mandates that drivers must either proceed straight ahead or turn right at the intersection.",
        "action": "Do not turn left. Choose between continuing forward or making a right turn."
    },
    33: {
        "id": 33,
        "code": "turn_right_ahead",
        "name": "Mandatory Turn Right Ahead",
        "category": "Mandatory",
        "shape": "Circular blue sign with an arrow pointing right",
        "description": "Mandates that all vehicles must turn right at the next intersection.",
        "action": "Indicate right and execute a right turn at the upcoming intersection. Straight or left travel is forbidden."
    },
    34: {
        "id": 34,
        "code": "turn_left_ahead",
        "name": "Mandatory Turn Left Ahead",
        "category": "Mandatory",
        "shape": "Circular blue sign with an arrow pointing left",
        "description": "Mandates that all vehicles must turn left at the next intersection.",
        "action": "Indicate left and execute a left turn at the upcoming intersection. Straight or right travel is forbidden."
    },
    35: {
        "id": 35,
        "code": "straight_ahead",
        "name": "Mandatory Straight Ahead Only",
        "category": "Mandatory",
        "shape": "Circular blue sign with an upward arrow",
        "description": "Mandates that all vehicles must continue straight ahead. Turning is prohibited.",
        "action": "Proceed only in the forward direction. Turning left or right is not permitted at this junction."
    },
    36: {
        "id": 36,
        "code": "straight_or_right",
        "name": "Mandatory Go Straight or Turn Right",
        "category": "Mandatory",
        "shape": "Circular blue sign with forward and right-angled arrows",
        "description": "Permits vehicles to either drive straight ahead or turn right at the intersection.",
        "action": "Left turns are prohibited. Select either the straight or right lane according to your intended destination."
    },
    37: {
        "id": 37,
        "code": "straight_or_left",
        "name": "Mandatory Go Straight or Turn Left",
        "category": "Mandatory",
        "shape": "Circular blue sign with forward and left-angled arrows",
        "description": "Permits vehicles to either drive straight ahead or turn left at the intersection.",
        "action": "Right turns are prohibited. Select either the straight or left lane according to your intended destination."
    },
    38: {
        "id": 38,
        "code": "keep_right",
        "name": "Mandatory Keep Right",
        "category": "Mandatory",
        "shape": "Circular blue sign with an arrow angled downward to the right",
        "description": "Directs traffic to pass on the right-hand side of a traffic island, bollard, or obstacle.",
        "action": "Steer to the right of the divider or obstacle. Do not pass on the left."
    },
    39: {
        "id": 39,
        "code": "keep_left",
        "name": "Mandatory Keep Left",
        "category": "Mandatory",
        "shape": "Circular blue sign with an arrow angled downward to the left",
        "description": "Directs traffic to pass on the left-hand side of an obstruction or roadway divider.",
        "action": "Steer to the left of the divider or obstacle as directed."
    },
    40: {
        "id": 40,
        "code": "roundabout_mandatory",
        "name": "Roundabout Mandatory (Traffic Circle)",
        "category": "Mandatory",
        "shape": "Circular blue sign with three counter-clockwise revolving arrows",
        "description": "Indicates a roundabout intersection where traffic moves in a circular direction.",
        "action": "Yield right-of-way to vehicles already circulating inside the roundabout before entering; circulate counter-clockwise."
    },
    41: {
        "id": 41,
        "code": "end_no_passing",
        "name": "End of No Passing Zone",
        "category": "De-restriction",
        "shape": "Circular white sign with a grey car and diagonal slash",
        "description": "Signals the conclusion of an overtaking prohibition for passenger cars.",
        "action": "You may overtake other vehicles when safe, subject to normal highway code rules."
    },
    42: {
        "id": 42,
        "code": "end_no_passing_for_trucks",
        "name": "End of No Passing for Heavy Vehicles",
        "category": "De-restriction",
        "shape": "Circular white sign with a grey truck and diagonal slash",
        "description": "Signals the conclusion of the overtaking prohibition for heavy vehicles exceeding 3.5 metric tons.",
        "action": "Heavy transport trucks may pass other vehicles if roadway conditions and safety permit."
    }
}


def get_sign_info(class_id: int) -> Dict[str, Any]:
    """Retrieve metadata for a class ID, with safe fallback."""
    if class_id in TRAFFIC_SIGN_METADATA:
        return TRAFFIC_SIGN_METADATA[class_id]
    return {
        "id": class_id,
        "code": f"class_{class_id}",
        "name": f"Traffic Sign Class #{class_id}",
        "category": "Unclassified / Custom",
        "shape": "Standard traffic sign",
        "description": "Traffic sign registered under class identifier " + str(class_id),
        "action": "Observe caution and comply with posted roadway instructions."
    }


def verify_labels_csv(csv_path: str) -> Dict[int, str]:
    """Read and verify the labels.csv file from the seed reference."""
    verified_mapping: Dict[int, str] = {}
    if not os.path.exists(csv_path):
        return verified_mapping

    with open(csv_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                cid = int(row["class_id"])
                cname = row["class_name"].strip()
                verified_mapping[cid] = cname
            except (ValueError, KeyError):
                continue
    return verified_mapping
