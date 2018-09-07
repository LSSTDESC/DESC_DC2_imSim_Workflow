

import glob

import parsl

import pathlib

from parsl.app.app import bash_app

parsl.set_stream_logger()

# import configuration after setting parsl logging, because interesting
# construction happens during the configuration

import configuration

parsl.load(configuration.parsl_config)


# /-terminated path to work and output base dir
cfg_work_and_out_path = "/projects/LSSTADSP_DESC/benc/"

# singularity image containing the ALCF_1.2i distro
cfg_singularity_img = cfg_work_and_out_path + "ALCF_1.2.simg"

cfg_singularity_url = "shub://benclifford/ALCF_1.2"

# set to true to use fake short sleep instead of singularity
cfg_fake = False

cfg_inst_cat_root = "/projects/LSSTADSP_DESC/ALCF_1.2i/inputs/"

@bash_app(executors=['submit-node'])
def cache_singularity_image(local_file, url):
    return "singularity build {} {}".format(local_file, url)


@bash_app(executors=['worker-nodes'])
def run_imsim_in_singularity_fake(nthreads: int, work_and_out_base: str, singularity_img_path: str, inst_cat: str, inst_cat_root: str, stdout=None, stderr=None):
    return "echo start a bash task; sleep 20s ; echo this is stdout ; (echo this is stderr >&2 ) ; false"

@bash_app(executors=['worker-nodes'])
def run_imsim_in_singularity(nthreads: int, work_and_out_base: str, singularity_img_path: str, inst_cat: str, inst_cat_root: str, stdout=None, stderr=None):
    stuff_a = inst_cat.replace(inst_cat_root, "ICROOT", 1)
    stuff_b = stuff_a.replace("/", "_")
    pathbase = "{}/run/{}/".format(work_and_out_base, stuff_b)
    outdir = pathbase + "out/"
    workdir = pathbase + "work/"
    return "singularity run -B {},{} {} --instcat {} --workdir {} --outdir {} --low_fidelity --subset_size 300 --subset_index 0 --file_id ckpt --processes {}".format(inst_cat_root, work_and_out_base, singularity_img_path, inst_cat, outdir, workdir, nthreads)


print("listing instance catalogs")
# This glob came from Jim Chiang
instance_catalogs = glob.glob('{}/DC2-R1*/0*/instCat/phosim_cat*.txt'.format(cfg_inst_cat_root))
print("there are {} instance catalogs to process".format(len(instance_catalogs)))

print("caching singularity image")


if not cfg_fake:
  singularity_future = cache_singularity_image(cfg_singularity_img, "shub://benclifford/ALCF_1.2i")

  singularity_future.result()


print("launching runs")

futures = []



for instance_catalog in instance_catalogs:
  print("launching a run for instance catalog {}".format(instance_catalog))
  if cfg_fake:
      p = run_imsim_in_singularity_fake
  else:
      p = run_imsim_in_singularity

  # TODO: factor this base 
  stuff_a = instance_catalog.replace(cfg_inst_cat_root, "ICROOT", 1)
  stuff_b = stuff_a.replace("/", "_")
  pathbase = "{}/run/{}/".format(cfg_work_and_out_path, stuff_b)
  outdir = pathbase + "out/"
  workdir = pathbase + "work/"

  pathlib.Path(workdir).mkdir(parents=True, exist_ok=True) 

  print("BENC: app in/out logging: will create path {}".format(workdir))
  ot = workdir + "task-stdout.txt"
  er = workdir + "task-stderr.txt"

 
  # is 63 the optimal number? this is just based on rumours from slack 
  future = p(63, cfg_work_and_out_path, cfg_singularity_img, instance_catalog, cfg_inst_cat_root, stdout=ot, stderr=er)
  print("launched a run for instance catalog {}".format(instance_catalog))
  futures.append(future)


for f in futures:
  print("waiting for a future")
  try:
    f.result()
  except Exception as e:
    print("future result gave exception {} which this script will ignore".format(e))

print("all futures have given a result or failed. the end")

