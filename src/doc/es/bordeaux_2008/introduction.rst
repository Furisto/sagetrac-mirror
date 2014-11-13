Introducci�n
============

�Que es Sage?
-------------

Sage (see http://sagemath.org) �s un sistema de software matem�tico
extenso para c�mputos en muchas �reas de la matem�tica pura y aplicada.
Programamos a Sage utilizando Python (see http://python.org),
el lenguaje de programaci�n de uso corriente, o su variante compilada Cython.
�s tambien muy f�cil usar eficientemente el c�digo escrito en C/C++ desde Sage.

El autor de �ste art�culo inici� el proyecto Sage en el 2005.

Sage es libre y de c�digo abierto, dando a entender que puedes cambiar cualquier parte
de Sage y redistribuir el resultado sin tener que pagar por alguna licencia,
y Sage tambien puede aventajar al poder del software matem�tico comercial
como el de Magma y Mathematica, si sucede que
tienes acceso a esos sistemas comerciales de c�digo cerrado.

�ste documento no asume alg�n conocimiento previo ya sea de Python o Sage.
Nuestra meta es ayudar a los que estudian teor�a de n�meros a hacer c�mputos que involucren
c�mpos de n�meros y formas modulares usando Sage.

TODO: Overview of Article

A medida que l�as este art�culo, por favor prueba cada ejemplo en Sage,
y asegurate que las cosas funcionen como yo pretendo, y h�z todos los ejercicios.
Adem�s, debes experimentar introduciendo ejemplos similares y
verificando que el resultado que obtengas est� de acuerdo con lo que esperas.

Usando Sage
-----------

Para usar Sage, inst�lalo en tu computador, y usa ya s�a la l�nea de comandos
o inicia el notebook de Sage tecleando ``notebook()`` en la l�nea de comandos.

Mostramos algunas sesiones de Sage a continuaci�n::

    sage: factor(123456)
    2^6 * 3 * 643


�sto significa que si tecl�as ``factor(123456)`` como entrada de datos en Sage, entonces
obtendr�s ``2^6 * 3 * 643`` como resultado. Si est�s usando la l�nea de comandos de Sage,
tecl�a ``factor(123456)`` y presiona enter; Si est�s usando el notebook de Sage a traves
de tu web browser, tecl�a ``factor(123456)`` en una celda de entrada de datos y presiona shift-enter;
en la celda de resultados ver�s ``2^6 * 3 * 643``.

Despu�s de probar el comando ``factor`` en el p�rrafo anterior
(�hazlo ahora!), debes tratar de factorizar otros n�meros.

.. note::

    �Qu� pasa si factorizas un n�mero negativo? �Un n�mero racional?


Tambi�n puedes dibujar gr�ficos tanto en 2D como en 3D usando Sage.
Por ejemplo, las siguiente entrada de datos traza el n�mero de divisores primos
de cada entero positivo hasta :math:`500`.

::

    sage: line([(n, len(factor(n))) for n in [1..500]])


Y este ejemplo dibuja un trazo similar en 3D::

    sage: v = [[len(factor(n*m)) for n in [1..15]] for m in [1..15]]
    sage: list_plot3d(v, interpolation_type='nn')


El Ecosistema Sage-Pari-Magma
-----------------------------

* *La diferencia principal entre Sage y Pari es que Sage es mucho m�s
  grande que Pari con un rango mucho m�s amplio de funcionalidad, y tiene
  muchos m�s tipos de datos y objetos mucho m�s estructurados.* Sage de hecho
  incluye a Pari, y una t�pica instalaci�n de Sage se lleva c�si un gigabyte de
  espacio en disco, mientras que una una t�pica instalaci�n de Pari �s mucho m�s liviana, usando
  s�lo unos cuantos megabytes. Hay muchos algor�tmos de teor�a de n�meros
  que est�n inclu�dos en Sage, los cuales nunca se han implementado en Pari, y
  Sage posee gr�ficos en 2D y 3D que pueden ser �tiles para visualizar
  ideas en teor�a de n�meros adem�s de un interf�z gr�fico del usuario. Tanto Pari como
  Sage son libres y de c�digo abierto, lo cual significa que cualquier persona puede leer o cambiar
  cualquier cosa en cualquiera de los dos programas y el software �s gr�tis.

* *La m�s grande diferencia entre Sage y Magma es de que Magma �s
  de c�digo cerrado, no es libre y �s dificil de extender por los usuarios.* Esto
  significa que la mayor parte de Magma no puede cambiarse excepto por los desarrolladores
  del n�cleo de Magma, ya que que la misma Magma tiene arriba de dos millones de l�neas
  de c�digo C compilado, combinados con c�si medio mill�n de l�neas de
  c�digo interpretado de Magma (que nadie puede leer ni modificar).
  Al dise�ar a Sage, tomamos algunas de las excelentes ideas de dise�o
  de Magma, tales como el padre, el elemento y la jerarqu�a de categor�as.

* *Cualquier matem�tico que seriamente quiere realizar trabajos de c�mputo extensos
  en teor�a algebraica de n�meros y geometr�a aritm�tica se le urge en�rgicamente
  a que se familiarize con los tres sistemas*, ya que todos ellos tienen sus pros
  y sus contras. Pari es pulcro y peque�o, Magma tiene funcionalidad �nica
  para c�mputos en geometr�a aritm�tica, y Sage tiene un amplio rango
  de funcionalidad en la mayor�a de las areas de la matem�tica, una gr�n
  comunidad de desarrolladores y un c�digo �nico y nuevo.
