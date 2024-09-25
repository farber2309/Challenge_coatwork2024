from VRPPD import *

target_folder = "training_data"

for instance in os.listdir(target_folder):
    instance_folder_path = target_folder + "/" + instance
    # print(instance_folder_path)
    prob = VRPPD()
    prob.read(instance_folder_path)
    prob.get_init_sol()
    val = prob.is_feasible()
    if not val:
        print("Infeasible : " + instance)
    else:
        print(prob.get_obj())
