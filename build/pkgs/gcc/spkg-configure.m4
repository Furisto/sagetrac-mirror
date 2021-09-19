AC_DEFUN([SAGE_NEEDS_CC], [
        AC_MSG_NOTICE([Sage needs working C/C++ compiler.])
        AC_MSG_ERROR([$1])
])

SAGE_SPKG_CONFIGURE_BASE([gcc], [
        AC_REQUIRE([AC_PROG_CC])
        AC_REQUIRE([AC_PROG_CPP])
        AC_REQUIRE([AC_PROG_CXX])
        AC_REQUIRE([AC_PROG_OBJC])
        AC_REQUIRE([AC_PROG_OBJCXX])

    # Figuring out if we are using clang instead of gcc.
    AC_LANG_PUSH(C)
    AX_COMPILER_VENDOR()
    IS_REALLY_GCC=no
    if test "x$ax_cv_c_compiler_vendor" = xgnu ; then
        IS_REALLY_GCC=yes
    fi
    AC_LANG_POP()

    # Save the value of CXX without special flags to enable C++11 support
    AS_VAR_SET([SAGE_CXX_WITHOUT_STD], [$CXX])
    AC_SUBST(SAGE_CXX_WITHOUT_STD)
    # Modify CXX to include an option that enables C++11 support if necessary
    AX_CXX_COMPILE_STDCXX_11([], optional)
    if test $HAVE_CXX11 != 1; then
        SAGE_NEEDS_CC([your C++ compiler does not support C++11])
    fi
    AC_SUBST(CXX)

    if test -z "$CC"; then
        SAGE_NEEDS_CC([a C compiler is missing])
    fi

    # Check for C99 support detected by the AC_PROG_CC macro.
    if test "x$ac_cv_prog_cc_c99" = xno; then
        SAGE_NEEDS_CC([your C compiler cannot compile C99 code])
    fi

    if test x$GXX != xyes; then
        SAGE_NEEDS_CC([your C++ compiler isn't GCC (GNU C++)])
    elif test $sage_spkg_install_gcc = yes; then
        # If we're installing GCC anyway, skip the rest of these version
        # checks.
        true
    elif test x$GCC != xyes; then
        SAGE_NEEDS_CC([your C compiler isn't GCC (GNU C)])
    else
        # Since sage_spkg_install_gcc is "no", we know that
        # at least C, C++ and Fortran compilers are available.
        # We also know that all compilers are GCC.

        # Find out the compiler versions:
        AX_GCC_VERSION()
        AX_GXX_VERSION()

        if test $IS_REALLY_GCC = yes ; then
            # Add the .0 because Debian/Ubuntu gives version numbers like
            # 4.6 instead of 4.6.4 (Trac #18885)
            AS_CASE(["$GXX_VERSION.0"],
                [[[0-3]].*|4.[[0-7]].*], [
                    # Install our own GCC if the system-provided one is older than gcc-4.8.
                    SAGE_NEEDS_CC([you have $CXX version $GXX_VERSION, which is quite old])
                ],
                [1[[2-9]].*], [
                    # Install our own GCC if the system-provided one is newer than 11.x.
                    # See https://trac.sagemath.org/ticket/29456
                    SAGE_NEEDS_CC([$CXX is g++ version $GXX_VERSION, which is too recent for this version of Sage])
                ],
                [4.[[8-9]].*|5.[[0-1]].*], [
                    # GCC less than 5.1 is not ready for AVX512.
                    sage_use_march_native=no
                ])
        fi

        # The following tests check that the version of the compilers
        # are all the same.
        if test "$GCC_VERSION" != "$GXX_VERSION"; then
            SAGE_NEEDS_CC([$CC ($GCC_VERSION) and $CXX ($GXX_VERSION) are not the same version])
        fi

    fi

    # Check that the assembler and linker used by $CXX match $AS and $LD.
    # See http://trac.sagemath.org/sage_trac/ticket/14296
    if test -n "$AS"; then
        CXX_as=`$CXX -print-prog-name=as 2>/dev/null`
        CXX_as=`command -v $CXX_as 2>/dev/null`
        cmd_AS=`command -v $AS`

        if ! (test "$CXX_as" = "" -o "$CXX_as" -ef "$cmd_AS"); then
            AC_MSG_NOTICE([       $CXX uses $CXX_as])
            AC_MSG_NOTICE([       \$AS equal to $AS])
            AC_MSG_ERROR([unset \$AS or set it to match your compiler's assembler])
        fi
    fi
    if test -n "$LD"; then
        CXX_ld=`$CXX -print-prog-name=ld 2>/dev/null`
        CXX_ld=`command -v $CXX_ld 2>/dev/null`
        cmd_LD=`command -v $LD`
        if ! (test "$CXX_ld" = "" -o "$CXX_ld" -ef "$cmd_LD"); then
            AC_MSG_NOTICE([       $CXX uses $CXX_ld])
            AC_MSG_NOTICE([       \$LD equal to $LD])
            AC_MSG_ERROR([unset \$LD or set it to match your compiler's linker])
        fi
    fi

    dnl A stamp file indicating that an existing, broken GCC install should be
    dnl cleaned up by make.
    if test x$SAGE_BROKEN_GCC = xyes; then
        AC_CONFIG_COMMANDS([broken-gcc], [
            # Re-run the check just in case, such as when re-running
            # config.status
            SAGE_CHECK_BROKEN_GCC()
            if test x$SAGE_BROKEN_GCC = xyes; then
                touch build/make/.clean-broken-gcc
            fi
        ], [
            SAGE_LOCAL="$SAGE_LOCAL"
            SAGE_SRC="$SAGE_SRC"
        ])
    fi

    # Determine which compiler flags should be set.
    if test x$sage_use_march_native = xno; then
        CFLAGS_MARCH=""
    elif test x$SAGE_FAT_BINARY = xyes; then
        CFLAGS_MARCH=""
    elif test x$sage_spkg_install_gcc = xyes; then
        CFLAGS_MARCH="-march=native"
    else
        AX_CHECK_COMPILE_FLAG("-march=native", [CFLAGS_MARCH="-march=native"], [CFLAGS_MARCH=""], [], [])
    fi
    AC_SUBST(CFLAGS_MARCH)

    # Determine wether compiler supports OpenMP.
    AC_LANG_PUSH([C])
    AX_OPENMP([
        AC_SUBST(OPENMP_CFLAGS)
    ])
    AC_LANG_POP()

    AC_LANG_PUSH([C++])
    AX_OPENMP([
        AC_SUBST(OPENMP_CXXFLAGS)
    ])
    AC_LANG_POP()


], , , [
    # Trac #27907: Find location of crti.o from the system CC, in case we build our own gcc
    AC_MSG_CHECKING([for the location of crti.o])
    CRTI=`$CC -print-file-name=crti.o 2>/dev/null || true`
    if test -n "$CRTI" ; then
        SAGE_CRTI_DIR=$(dirname -- "$CRTI")
        if test "$SAGE_CRTI_DIR" = "." ; then
            SAGE_CRTI_DIR=
        fi
    fi
    AC_SUBST(SAGE_CRTI_DIR)
    AC_MSG_RESULT($SAGE_CRTI_DIR)
])
