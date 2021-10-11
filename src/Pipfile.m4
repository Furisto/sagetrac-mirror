## Pipfile with all dependencies of sagelib and version information as free as possible
## (for developers to generate a dev environment)
[[source]]
name = "pypi"
url = "https://pypi.org/simple"
verify_ssl = true

[dev-packages]
## We do not list packages that are already declared as install_requires
## in setup.cfg
pycodestyle = "*"
tox = "*"
pytest = "*"
rope = "*"
six = "*"
rstcheck = "*"

[packages]
## We do not list packages that are already declared as install_requires
## in setup.cfg

[packages.e1839a8]
path = "."
editable = true

[packages.8c46424]
path = "./../pkgs/sage-conf"
editable = true
