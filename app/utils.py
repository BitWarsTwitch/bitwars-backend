def compute_damage_based_on_attack_id(attack_id):
    damage_mapping = {
        1: 1,
        2: 2,
        3: 2,
        4: 5,
        5: 5,
        6: 5,
        7: 5,
        8: 10,
        9: 25,
    }
    return damage_mapping.get(attack_id, 0)
