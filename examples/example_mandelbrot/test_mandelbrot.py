import random
import multiprocessing
import os
import tempfile
import shutil
import pytest

def test_mandelbrot():
    from mountaintools import client as mt
    import mlprocessors as mlpr
    from .mandelbrot import compute_mandelbrot, show_mandelbrot, combine_subsampled_mandelbrot, ComputeMandelbrot, compute_mandelbrot_parallel
    import numpy as np

    result=ComputeMandelbrot.execute(
        num_iter=10,
        num_x=50,
        output_npy=dict(ext='.npy', upload=True)
    )
    X=np.load(mt.realizeFile(result.outputs['output_npy']))

    Y=compute_mandelbrot_parallel(
        num_iter=10,
        num_x=50,
        num_parallel=3,
        compute_resource=None,
        _force_run=True
    )

    Z=compute_mandelbrot_parallel(
        num_iter=10,
        num_x=50,
        num_parallel=3,
        compute_resource=None,
        _force_run=False
    )

    print(X.shape, Y.shape, Z.shape)

    assert np.all(np.isclose(X,Y))
    assert np.all(np.isclose(X,Z))

@pytest.mark.compute_resource
def test_mandelbrot_compute_resource():
    with LocalComputeResource(num_parallel=4) as compute_resource:
        from mountaintools import client as mt
        import mlprocessors as mlpr
        from .mandelbrot import compute_mandelbrot, show_mandelbrot, combine_subsampled_mandelbrot, ComputeMandelbrot, compute_mandelbrot_parallel
        import numpy as np

        result=ComputeMandelbrot.execute(
            num_iter=10,
            num_x=50,
            output_npy=dict(ext='.npy', upload=True)
        )
        X=np.load(mt.realizeFile(result.outputs['output_npy']))

        Y=compute_mandelbrot_parallel(
            num_iter=10,
            num_x=50,
            num_parallel=3,
            compute_resource=compute_resource,
            _force_run=True
        )

        assert np.all(np.isclose(X,Y))

class LocalComputeResource():
    def __init__(self,num_parallel):
        self._num_parallel=num_parallel
    def __enter__(self):
        from mountaintools import client as mt
        resource_name='local_resource_'+_random_string(6)
        self._process=multiprocessing.Process(target=_run_local_compute_resource, args=(resource_name,self._num_parallel))
        self._process.start()
        return dict(resource_name=resource_name,collection=None,share_id=None)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._process.terminate()

class TemporaryDirectory():
    def __init__(self):
        pass
    def __enter__(self):
        self._path=tempfile.mkdtemp()
        return self._path

    def __exit__(self, exc_type, exc_val, exc_tb):
        shutil.rmtree(self._path)

    def path(self):
        return self._path


def _run_local_compute_resource(resource_name, num_parallel):
    import mlprocessors as mlpr
    from mountaintools import client as mt
    server=mlpr.ComputeResourceServer(
        resource_name=resource_name,
        collection=None,
        share_id=None
    )
    server.setNumParallel(num_parallel)
    server.start()

def _random_string(num):
    return ''.join(random.choices('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ', k=num))
