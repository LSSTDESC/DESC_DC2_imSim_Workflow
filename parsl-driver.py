
import mpix_local

import parsl

from parsl.app.app import bash_app

parsl.set_stream_logger()

parsl.load(mpix_local.config)


# in testing without parsl, run something liek this:
# aprun -n 1 -N 1 -d 64 -j 1 -cc depth singularity run benc-cached.simg ~/desc/benc.instcat/000025/instCat/phosim_cat_32678.txt ~/desc/tmp-workdir10/ ~/desc/tmp-outdir10/ 63 0 10000 0 benc_chk_base
# inside ,parsl, the aprun shoudl already have happened as part
# of the mpix_local config

@bash_app
def run_imsim_in_singularity(work_out_dir_n: int, nthreads: int):
    return "singularity run ~/desc2.0i/ALCF_1.2i/benclifford-ALCF.simg --instcat ~/desc/benc.instcat/000025/instCat/phosim_cat_32678.txt --workdir ~/desc/tmp-workdir{}/ --outdir ~/desc/tmp-outdir{}/ --low_fidelity --subset_size 300 --subset_index 0 --file_id CHKPT --processes {}".format(work_out_dir_n, work_out_dir_n, nthreads)

    # return "singularity run /home/benc/desc2.0i/ALCF_1.2i/benc-cached.simg ~/desc/benc.instcat/000025/instCat/phosim_cat_32678.txt ~/desc2.0i/runtime/workdir-{}/ ~/desc2.0i/runtime/outdir-{}/ {} 0 10000 0 checkpoint_".format(work_out_dir_n, work_out_dir_n, nthreads)

print("launching urn")
future = run_imsim_in_singularity(17, 63)
print("launched run ... waiting for result")
future.result()
print("result received. the end")

