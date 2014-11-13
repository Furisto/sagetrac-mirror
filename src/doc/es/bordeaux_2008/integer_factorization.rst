Factorizaci�n De Enteros
========================


Criba Cuadr�tica
----------------

La criba cuadr�tica de Bill Hart est� inclu�da en Sage. La criba cuadr�tica
�s el mejor algor�tmo para factorizar n�meros de la forma :math:`pq` de 
hasta alrededor de 100 d�gitos. Involucra la b�squeda de relaciones, resolviendo
un problema de �lgebra lineal modulo :math:`2`, luego factorizando :math:`n`
utilizando una relaci�n :math:`x^2 \equiv y^2 \mod n`.

::

    sage: qsieve(next_prime(2^90)*next_prime(2^91), time=True)   # a�n sin probar
    ([1237940039285380274899124357, 2475880078570760549798248507],
     '14.94user 0.53system 0:15.72elapsed 98%CPU (0avgtext+0avgdata 0maxresident)k')

El uso de ``qsieve`` �s dos veces m�s r�pido que el comando general ``factor`` de Sage en
este ejemplo. N�tese que el comando general ``factor`` de Sage no hace nada m�s que
invocar a la funci�n ``factor`` de la biblioteca en C de Pari.

::

    sage: time factor(next_prime(2^90)*next_prime(2^91))     # a�n sin probar
    CPU times: user 28.71 s, sys: 0.28 s, total: 28.98 s
    Wall time: 29.38 s
    1237940039285380274899124357 * 2475880078570760549798248507

Obviamente, el comando ``factor`` de Sage no debiera solamente llamar a Pari, pero
todav�a nadie se ha acercado a reescribirla.

GMP-ECM
-------

El m�todo GMP-ECM de Paul Zimmerman est� inclu�do en Sage. El algor�tmo
de factorizaci�n para curvas el�pticas (ECM) es el mejor algor�tmo para factorizar
n�meros de la forma :math:`n=pm`, donde :math:`p` no es "demasiado
grande". ECM es un algor�tmo que se debe a Hendrik Lenstra, que funciona
"fingiendo" que :math:`n` �s primo, escogiendo una curva el�ptica al azar
sobre :math:`\ZZ/n\ZZ` y efectuando aritm�tica sobre esa curva
--si algo sale mal cuando se efect�a la aritm�tica, factorizamos a
:math:`n`.

En el siguiente ejemplo, GMP-ECM est� por encima de 10 veces m�s r�pido que
la funci�n gen�rica ``factor`` de Sage. De nuevo, �sto enfatiza que el
comando gen�rico ``factor`` de Sage se beneficiar�a de una reescritura
que utilice a GMP-ECM y a qsieve.

::

    sage: time ecm.factor(next_prime(2^40) * next_prime(2^300))    # not tested
    CPU times: user 0.85 s, sys: 0.01 s, total: 0.86 s
    Wall time: 1.73 s
    [1099511627791,
     2037035976334486086268445688409378161051468393665936250636140449354381299763336706183397533]
    sage: time factor(next_prime(2^40) * next_prime(2^300))        # not tested
    CPU times: user 23.82 s, sys: 0.04 s, total: 23.86 s
    Wall time: 24.35 s
    1099511627791 * 2037035976334486086268445688409378161051468393665936250636140449354381299763336706183397533
