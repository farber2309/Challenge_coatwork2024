from VRPPD import *

target_folder = "training_data"

def test_misc():
    iter = 0
    for instance in os.listdir(target_folder):
        instance_folder_path = target_folder + "/" + instance
        iter += 1
        if iter == 1:
            prob = VRPPD()
            prob.read(instance_folder_path)
        if iter == 4:
            instance_folder_path = target_folder + "/" + instance
            # print(instance_folder_path)
            prob = VRPPD()
            prob.read(instance_folder_path)
            print(prob.DISTANCES)
            prob.naive_sol()
            val = True
            val = prob.is_feasible()
            # print(prob.routes)
            if not val:
                print("Infeasible : " + instance)
            else:
                print(prob.get_obj())
    return

def test_mip():
    iter = 0
    for instance in os.listdir(target_folder):
        print(instance)
        instance_folder_path = target_folder + "/" + instance
        prob = VRPPD()
        prob.read(instance_folder_path)
        prob.mip_solve()
        iter += 1
    return

def test_b6bc5f29():
    instance = "b6bc5f29-f105-48aa-92a3-eafc3e625253"
    instance_folder_path = target_folder + "/" + instance
    prob = VRPPD()
    prob.read(instance_folder_path)
    prob.mip_solve()

test_b6bc5f29()

