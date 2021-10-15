#
# SYNOPSIS
#
#   SAGE_PYTHON_PACKAGE_CHECK(package)
#
# DESCRIPTION
#
#   Determine if the system copy of a python package can be used by sage.
#
#   This macro uses setuptools.version's pkg_resources to check that the
#   "install-requires.txt" file for the named package is satisfied, and
#   it can typically fail in four ways:
#
#     1. If --enable-system-site-packages was not passed to ./configure,
#
#     2. If we are not using the system python (no $PYTHON_FOR_VENV),
#
#     3. If we are unable to create a venv with the system python,
#
#     4. If setuptools is not available to the system python,
#
#     5. If the contents of install-requires.txt are not met (wrong
#        version, no version, etc.) by the system python.
#
#   In any of those cases, we set sage_spkg_install_$package to "yes"
#   so that the corresponding SPKG is installed. Otherwise, we do
#   nothing, since the default value of sage_spkg_install_$package
#   is "no" (to use the system copy).
#
#   The SAGE_SPKG_CONFIGURE_PYTHON3() macro is AC_REQUIRE'd to ensure
#   that $PYTHON_FOR_VENV is available, if it is going to be available.
#   The check is run inside a new venv, and with the PYTHONUSERBASE
#   variable poisoned in the same manner as sage-env poisons it, to
#   ensure that the ./configure- and run-time views of the system
#   are as similar as possible.
#

AC_DEFUN([SAGE_PYTHON_PACKAGE_CHECK], [
  AS_IF([test "${enable_system_site_packages}" = "yes"], [
    AC_REQUIRE([SAGE_SPKG_CONFIGURE_PYTHON3])

    dnl We run this check inside a python venv, because that's ultimately
    dnl how the system $PYTHON_FOR_VENV will be used.
    AC_MSG_CHECKING([if we can create a python venv in config.venv])

    dnl Use --clear because ./configure typically clobbers its output files.
    AS_IF(["${PYTHON_FOR_VENV}" -m venv --system-site-packages dnl
                                        --clear                dnl
                                        --without-pip          dnl
					config.venv], [
      AC_MSG_RESULT(yes)
      dnl strip all comments from install-requires.txt; this should leave
      dnl only a single line containing the version specification for this
      dnl package.
      SAGE_PKG_VERSPEC=$(sed '/^#/d' "./build/pkgs/$1/install-requires.txt")
      AC_MSG_CHECKING([for python package $1 ("${SAGE_PKG_VERSPEC}")])

      dnl To prevent user-site (pip install --user) packages from being
      dnl detected as "system" packages, we poison PYTHONUSERBASE. The
      dnl sage-env script also does this at runtime; we mimic that
      dnl implementation to ensure that the behaviors at ./configure and
      dnl runtime are identical. Beware that (as in sage-env) the poisoning
      dnl is skipped if PYTHONUSERBASE is non-empty. In particular, if the
      dnl user points PYTHONUSERBASE to any path (even the default), then
      dnl his local pip packages will be detected.
      PYTHONUSERBASE_SAVED="${PYTHONUSERBASE}"
      AS_IF([test -z "${PYTHONUSERBASE}"], [
        PYTHONUSERBASE="${HOME}/.sage/local"
      ])

      AS_IF(
        [PYTHONUSERBASE="${PYTHONUSERBASE}" config.venv/bin/python3 -c dnl
           "from setuptools.version import pkg_resources;              dnl
            pkg_resources.require('${SAGE_PKG_VERSPEC}'.splitlines())" dnl
	 2>/dev/null],
        [AC_MSG_RESULT(yes)],
        [AC_MSG_RESULT(no); sage_spkg_install_$1=yes]
      )

      PYTHONUSERBASE="${PYTHONUSERBASE_SAVED}"
    ], [
      dnl failed to create a venv for some reason
      AC_MSG_RESULT(no)
      sage_spkg_install_$1=yes
    ])

    rm -rf config.venv
  ], [
    sage_spkg_install_$1=yes
  ])
])
