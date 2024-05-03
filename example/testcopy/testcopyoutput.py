#
# import os
# import shutil
# path = "C:\\Users\\Twhp\\PycharmProjects\\GoldRushTrader\\example\\testcopy\\outputs_bt"
# folder = "C:\\Users\\Twhp\\PycharmProjects\\GoldRushTrader\\example\\test_websvr\\bt_deploy\\admin\\36442f03c8e74081cacc18716ee7b7e9\\backtests\\e459d7fcd2bbdc84f35d46460d95b590"
# old_output = os.path.join(folder, "outputs_bt")
# def ignore_existing_files(folder, files):
#     existing_files = set(os.listdir(folder))
#     return set(files) - existing_files
# shutil.copytree(old_output, path, dirs_exist_ok=True)


index_codes = []
start_index = 399662
end_index = 399702

for i in range(start_index, end_index + 1):
    index_code = {
        "value": f"SZSE.IDX.{i}",
        "label": f"SZSE.IDX.{i}"
    }
    index_codes.append(index_code)

print(index_codes)