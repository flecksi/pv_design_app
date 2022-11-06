import PyInstaller.__main__

# https://pyinstaller.readthedocs.io/en/stable/usage.html
#
# --onefile has the benefit of only generating a single file
#   but the startup is very slow each time b/c of uncompressing

# scipy_hidden = [
#     "scipy._lib.messagestream",
#     "scipy",
#     "scipy.signal",
#     "scipy.signal.bsplines",
#     "scipy.special",
#     "scipy.special._ufuncs_cxx",
#     "scipy.linalg.cython_blas",
#     "scipy.linalg.cython_lapack",
#     "scipy.integrate",
#     "scipy.integrate.quadrature",
#     "scipy.integrate.odepack",
#     "scipy.integrate._odepack",
#     "scipy.integrate.quadpack",
#     "scipy.integrate._quadpack",
#     "scipy.integrate._ode",
#     "scipy.integrate.vode",
#     "scipy.integrate._dop",
#     "scipy._lib",
#     "scipy._build_utils",
#     "scipy.__config__",
#     "scipy.integrate.lsoda",
#     "scipy.cluster",
#     "scipy.constants",
#     "scipy.fftpack",
#     "scipy.interpolate",
#     "scipy.io",
#     "scipy.linalg",
#     "scipy.misc",
#     "scipy.ndimage",
#     "scipy.odr",
#     "scipy.optimize",
#     "scipy.setup",
#     "scipy.sparse",
#     "scipy.spatial",
#     "scipy.special",
#     "scipy.stats",
#     "scipy.version",
# ]

# hidden_list = []

# for i in scipy_hidden:
#     hidden_list.append("--hidden-import")
#     hidden_list.append(f"{i}")

PyInstaller.__main__.run(
    [
        "app.py",
        "-y",
        # "--onefile",
        "--name",
        "pv_design_app",
        # "--hidden-import",
        # "scipy.version",
        # *hidden_list,
        # "--key",
        # "0123456789012345",
        # "--add-data",
        # "../test_inputdata;./test_inputdata",
    ]
)
