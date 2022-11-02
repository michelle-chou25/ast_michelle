import json
import os


def crate(dataset_path, flag='one_mic', dataset='train'):
    result_json = {'data': []}
    ng_path = os.path.join(dataset_path, 'NG')
    ok_path = os.path.join(dataset_path, 'OK')

    ng_folders = os.listdir(ng_path)
    ok_folders = os.listdir(ok_path)
    all_num_ng = 0
    all_num_ok = 0
    for one_folder in ng_folders:
        files = os.listdir(os.path.join(ng_path, one_folder))
        print("NG:", one_folder, "---------", len(files))
        all_num_ng += len(files)
        for one_file in files:
            result_json['data'].append({'wav': os.path.join(ng_path, one_folder, one_file),
                                        'labels': '/m/ng',
                                        })
    for one_folder in ok_folders:
        files = os.listdir(os.path.join(ok_path, one_folder))
        print("OK:", one_folder, "---------", len(files))
        all_num_ok += len(files)
        for one_file in files:
            result_json['data'].append({'wav': os.path.join(ok_path, one_folder, one_file),
                                        'labels': '/m/ok',
                                        })
    print(f'{dataset} NG Total:', all_num_ng)
    print(f'{dataset} OK Total:', all_num_ok)
    print(f'{dataset} all Total:', all_num_ng + all_num_ok)
    if flag == 'one_mic':
        with open(f'../wz_relay/wz_relay_{dataset}.json', 'w') as fp:
            json.dump(result_json, fp)
    elif flag == 'dual_mic':
        with open(f'../wz_relay_dual/wz_relay_{dataset}.json', 'w') as fp:
            json.dump(result_json, fp)


crate(r"../dataset/dual_mic/train", flag='dual_mic', dataset='train')
print('####################################################')
crate(r"../dataset/dual_mic/val", flag='dual_mic', dataset='val')
