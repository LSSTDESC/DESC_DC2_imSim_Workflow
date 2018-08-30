
import configuration

import glob

import parsl

from parsl.app.app import bash_app

parsl.set_stream_logger()

parsl.load(configuration.parsl_config)


# /-terminated path to work and output base dir
cfg_work_and_out_path = "~benc/desc/"

# singularity image containing the ALCF_1.2i distro
cfg_singularity_img = cfg_work_and_out_path + "ALCF_1.2.simg"

cfg_singularity_url = "shub://benclifford/ALCF_1.2"

# set to true to use fake short sleep instead of singularity
cfg_fake = False

@bash_app(executors=['submit-node'])
def cache_singularity_image(local_file, url):
    return "singularity build {} {}".format(local_file, url)


@bash_app(executors=['worker-nodes'])
def run_imsim_in_singularity_fake(nthreads: int, work_and_out_base: str, singularity_img_path: str, inst_cat: str):
    return "sleep 20s"

@bash_app(executors=['worker-nodes'])
def run_imsim_in_singularity(nthreads: int, work_and_out_base: str, singularity_img_path: str, inst_cat: str):
    pathbase = "{}/run/".format(work_and_out_base)
    outdir = pathbase + "out/"
    workdir = pathbase + "work/"
    return "singularity run {} --instcat {} --workdir {} --outdir {} --low_fidelity --subset_size 300 --subset_index 0 --file_id ckpt --processes {}".format(singularity_img_path, inst_cat, outdir, workdir, nthreads)


print("listing instance catalogs")
# This glob came from Jim Chiang
instance_catalogs = glob.glob('/projects/LSSTADSP_DESC/ALCF_1.2i/inputs/DC2-R1*/0*/instCat/phosim_cat*.txt')
print("there are {} instance catalogs to process".format(len(instance_catalogs)))

print("caching singularity image")


singularity_future = cache_singularity_image(cfg_singularity_img, "shub://benclifford/ALCF_1.2i")

singularity_future.result()


print("launching runs")

res = []




for instance_catalog in instance_catalogs:
  print("launching a run for instance catalog {}".format(instance_catalog))
  if cfg_fake:
      p = run_imsim_in_singularity_fake
  else:
      p = run_imsim_in_singularity
  
  # is 63 the optimal number? this is just based on rumours from slack 
  future = p(63, cfg_work_and_out_path, cfg_singularity_img, instance_catalog)
  print("launched a run for instance catalog {}")
  futures.append(future)


for f in res:
  print("waiting for a future")
  f.result()

print("result received. the end")

