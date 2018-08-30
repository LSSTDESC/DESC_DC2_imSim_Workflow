
import configuration

import parsl

from parsl.app.app import bash_app

parsl.set_stream_logger()

parsl.load(configuration.parsl_config)


# /-terminated path to work and output base dir
cfg_work_and_out_path = "~benc/desc/"

# singularity image containing the ALCF_1.2i distro
cfg_singularity_img = "~benc/desc2.0i/ALCF_1.2i/benclifford-ALCF.simg"

#  test instance catalog - TO BE REPLACED BY GENERATED LIST
cfg_inst_cat = "~benc/desc/benc.instcat/000025/instCat/phosim_cat_32678.txt"

# for load testing, run this many times:
cfg_repeated_runs = 7

@bash_app
def run_imsim_in_singularity(work_out_dir_n: int, nthreads: int, pseudo_catalog: int, work_and_out_base: str, singularity_img_path: str, inst_cat: str):
    pathbase = "{}/run-{}-{}/".format(work_and_out_base, work_out_dir_n, pseudo_catalog)
    outdir = pathbase + "out/"
    workdir = pathbase + "work/"
    return "singularity run {} --instcat {} --workdir {} --outdir {} --low_fidelity --subset_size 300 --subset_index 0 --file_id ckpt --processes {}".format(singularity_img_path, inst_cat, outdir, workdir, nthreads)

    # return "singularity run /home/benc/desc2.0i/ALCF_1.2i/benc-cached.simg ~/desc/benc.instcat/000025/instCat/phosim_cat_32678.txt ~/desc2.0i/runtime/workdir-{}/ ~/desc2.0i/runtime/outdir-{}/ {} 0 10000 0 checkpoint_".format(work_out_dir_n, work_out_dir_n, nthreads)

print("launching runs")

res = []

for pseudo_catalog in range(0,cfg_repeated_runs):
  print("launching a run")
  future = run_imsim_in_singularity(18, 63, pseudo_catalog, cfg_work_and_out_path, cfg_singularity_img, cfg_inst_cat)
  print("launched a run")
  res.append(future)


for f in res:
  print("waiting for a future")
  f.result()

print("result received. the end")

