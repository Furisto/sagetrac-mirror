SAGE_SPKG_CONFIGURE([maxima], [
  SAGE_SPKG_DEPCHECK([ecl], [
    dnl First check for the "maxima" executable in the user's PATH, because
    dnl we still use pexpect to communicate with it in a few places. We pass
    dnl the "-l ecl" flag here to ensure that the standalone executable also
    dnl supports ECL.
    AC_MSG_CHECKING(if "maxima -l ecl" works)
    AS_IF([! maxima -l ecl -q -r 'quit();' \
             >&AS_MESSAGE_LOG_FD 2>&AS_MESSAGE_LOG_FD], [
      AC_MSG_RESULT(no)
      sage_spkg_install_maxima=yes
    ], [
      AC_MSG_RESULT(yes)
      dnl If we have the executable, check also for the ECL library.
      AC_MSG_CHECKING([if ECL can "require" the maxima module])
      AS_IF([ecl --eval "(require 'maxima)" --eval "(quit)" \
               >&AS_MESSAGE_LOG_FD 2>&AS_MESSAGE_LOG_FD], [
        AC_MSG_RESULT(yes)
      ], [
	AC_MSG_RESULT(no)
	sage_spkg_install_maxima=yes
      ])
    ])
  ])
],[],[],[
  # post-check
  AS_IF([test x$sage_spkg_install_maxima = xyes], [
    dnl Leaving this variable empty will tell sagelib to load
    dnl the maxima library (within ECL) by name instead of by
    dnl absolute path.
    SAGE_MAXIMA_FAS='${prefix}'/lib/ecl/maxima.fas
  ])
  AC_SUBST(SAGE_MAXIMA_FAS, "${SAGE_MAXIMA_FAS}")
])

