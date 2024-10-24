def compute_damage_based_on_attack_id(attack_id):
    damage_mapping = {
        1: 25,
        2: 50,
        3: 50,
        4: 100,
        5: 100,
        6: 100,
        7: 250,
        8: 500,
        9: 1000,
    }
    return damage_mapping.get(attack_id, 0)
