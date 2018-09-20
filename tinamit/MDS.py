import os
import tempfile

from Análisis.sintaxis import Ecuación
from cositas import guardar_archivo
from tinamit.Modelo import Modelo
from tinamit.config import _


class EnvolturaMDS(Modelo):
    """
    Esta clase sirve para representar modelo de dinámicas de los sistemas (EnvolturasMDS). Se debe crear una subclase para cada
    tipo_mod de EnvolturasMDS. Al momento, el único incluido es VENSIM.
    """

    def __init__(símismo, archivo, nombre='mds', **ops_mód):
        """
        Iniciamos el modelo DS.

        :param archivo: El fuente con el modelo DS.
        :type archivo: str
        """

        if not os.path.isfile(archivo):
            raise FileNotFoundError(_('El fuente "{}" no existe.').format(archivo))

        # Acordarse de dónde venimos
        símismo.archivo = archivo

        # Generar el modelo externo
        símismo.mod = símismo._generar_mod(archivo, **ops_mód)

        #
        símismo.editado = False

        # Modelos DS se identifican por el nombre 'mds'.
        super().__init__(nombre=nombre)

    def constantes(símismo):
        return [var for var, d_var in símismo.variables.items() if
                'tipo_mod' in d_var and d_var['tipo_mod'] == 'constante']

    def iniciales(símismo):
        return [var for var, d_var in símismo.variables.items() if
                'tipo_mod' in d_var and d_var['tipo_mod'] == 'inicial']

    def niveles(símismo):
        return [var for var, d_var in símismo.variables.items() if 'tipo_mod' in d_var and d_var['tipo_mod'] == 'nivel']

    def flujos(símismo):
        return [var for var, d_var in símismo.variables.items() if 'tipo_mod' in d_var and d_var['tipo_mod'] == 'flujo']

    def auxiliares(símismo):
        return [var for var, d_var in símismo.variables.items() if
                'tipo_mod' in d_var and d_var['tipo_mod'] == 'auxiliar']

    def hijos(símismo, var):
        var = símismo.valid_var(var)
        return símismo.variables[var]['hijos']

    def parientes(símismo, var):
        var = símismo.valid_var(var)
        return símismo.variables[var]['parientes']

    def editable(símismo):
        return False

    def editar_ec(símismo, var, ec):

        if not símismo.editable():
            raise NotImplementedError(_('El modelo "{}" no se puede editar.').format(str(símismo)))

        var = símismo.valid_var(var)
        try:
            obj_ec = Ecuación(ec)
            vars_ec = obj_ec.variables()
            for v in vars_ec:
                símismo.valid_var(v)

        except ValueError:
            raise ValueError(_('Error sintáctico en la ecuación "{}"').format(ec))

        símismo.variables[var]['ec'] = ec
        símismo.editado = True

    def guardar_mod(símismo, archivo=None):

        if archivo is None:
            archivo = símismo.archivo

        if símismo.editado:
            guardar_archivo(arch=archivo, contenido=símismo._generar_archivo_mod())
            símismo.mod = símismo._generar_mod(archivo)
            símismo.editado = False

    def _generar_archivo_mod(símismo):
        raise NotImplementedError

    def _generar_mod(símismo, archivo, **ops_mód):
        raise NotImplementedError

    def _inic_dic_vars(símismo):
        """
        Este método se deja a las subclases de :class:`~tinamit.EnvolturasMDS.EnvolturasMDS` para implementar. Además de
        los diccionarios de variables normales, debe establecer `símismo.constantes`, `símismo.flujos`,
        `símismo.niveles`, `símismo.editables`, y `símismo.auxiliares`. Este último
        debe tener las llaves "hijos", "parientes" y "ec".

        Ver :func:`Modelo.Modelo._inic_dic_vars` para más información.
        """

        raise NotImplementedError

    def _verificar_dic_vars(símismo, reqs=None):

        requísitos = ['ec', 'hijos', 'parientes', 'tipo_mod', 'info']
        if reqs is not None:
            requísitos += reqs

        super()._verificar_dic_vars(reqs=requísitos)

        mens_err = _('Error en las relaciones pariente-hijos de variable "{}"')
        for var in símismo.variables:
            parientes = símismo.parientes(var)
            hijos = símismo.hijos(var)
            if not all(var in símismo.hijos(p) for p in parientes):
                raise ValueError(mens_err.format(var))
            if not all(var in símismo.parientes(h) for h in hijos):
                raise ValueError(mens_err.format(var))

    def _reinic_vals(símismo):
        raise NotImplementedError

    def _propagar_vals_vars_inic(símismo, valores):

        for v in símismo.iniciales():
            hijos = símismo.hijos(v)
            val = símismo.obt_val_actual_var(v)
            símismo._act_vals_dic_var({hj: val for hj in hijos})

    def unidad_tiempo(símismo):
        """
        Cada envoltura de programa DS debe implementar este metodo para devolver las unidades de tiempo del modelo DS
        cargado.

        :return: Las unidades del modelo DS cargado.
        :rtype: str

        """
        raise NotImplementedError

    def _iniciar_modelo(símismo, tiempo_final, nombre_corrida, vals_inic):
        """
        Este método se deja a las subclases de :class:`~tinamit.EnvolturasMDS.EnvolturasMDS` para implementar. Notar que la
        implementación de este método debe incluir la aplicación de valores iniciales.

        Ver :func:`Modelo.Modelo.iniciar_modelo` para más información.

        :param nombre_corrida: El nombre de la corrida (útil para guardar resultados).
        :type nombre_corrida: str

        :param tiempo_final: El tiempo final de la simulación.
        :type tiempo_final: int

        """
        if símismo.editado:
            ext = os.path.splitext(símismo.archivo)[1]
            arch_temp = tempfile.NamedTemporaryFile('w', encoding='UTF-8', suffix=ext, delete=False).name
            símismo.guardar_mod(arch_temp)

            símismo.mod = símismo._generar_mod(archivo=arch_temp)

            os.remove(arch_temp)

        super()._iniciar_modelo(tiempo_final, nombre_corrida, vals_inic)

    def _cambiar_vals_modelo_externo(símismo, valores):
        """
        Este método se deja a las subclases de :class:`~tinamit.EnvolturasMDS.EnvolturasMDS` para implementar.

        Ver :func:`Modelo.Modelo.cambiar_vals_modelo` para más información.

        :param valores: El diccionario de valores para cambiar.
        :type valores: dict

        """
        raise NotImplementedError

    def _incrementar(símismo, paso, guardar_cada=None):
        """
        Este método se deja a las subclases de :class:`~tinamit.EnvolturasMDS.EnvolturasMDS` para implementar.

        Debe avanzar la simulación del modelo DS de ``paso`` unidades de tiempo.  Ver
        :func:`Modelo.Modelo.incrementar` para más información.

        :param paso: El paso con cual incrementar el modelo.
        :type paso: int

        """
        raise NotImplementedError

    def _leer_vals(símismo):
        """
        Este método se deja a las subclases de :class:`~tinamit.EnvolturasMDS.EnvolturasMDS` para implementar.

        Debe leer los valores de los variables en el modelo EnvolturasMDS. Si es más fácil, puede simplemente leer los valores
        de los variables que están en la lista ``EnvolturasMDS.vars_saliendo`` (los variables del DS que están
        conectados con el modelo biofísico).

        Ver :func:`Modelo.Modelo.leer_vals` para más información.

        """
        raise NotImplementedError

    def cerrar_modelo(símismo):
        """
        Este método se deja a las subclases de :class:`~tinamit.EnvolturasMDS.EnvolturasMDS` para implementar.

        Debe llamar acciones necesarias para terminar la simulación y cerrar el modelo DS, si aplican.

        Ver :func:`Modelo.Modelo.cerrar_modelo` para más información.

        """
        raise NotImplementedError

    def __getinitargs__(símismo):
        return símismo.archivo,


class MDSEditable(EnvolturaMDS):
    def __init__(símismo, archivo, nombre='mds'):
        super().__init__(archivo=archivo, nombre=nombre)

        from tinamit.EnvolturasMDS import generar_mds
        símismo.mod = None  # type: EnvolturaMDS
        símismo._estab_mod(generar_mds(archivo=archivo, editables=False))
        símismo.combin_incrs = símismo.mod.combin_pasos

        símismo.editado = False

    def _estab_mod(símismo, mod):
        """

        Parameters
        ----------
        mod: EnvolturaMDS

        Returns
        -------

        """
        símismo.mod = mod
        mod.mem_vars = símismo.mem_vars
        mod.vars_saliendo = símismo.vars_saliendo
        mod.variables = símismo.variables

    def _act_vals_dic_var(símismo, valores):
        símismo.mod._act_vals_dic_var(valores=valores)
        super()._act_vals_dic_var(valores)

    def _reinic_vals(símismo):
        símismo.mod._reinic_vals()

    def _inic_dic_vars(símismo):
        raise NotImplementedError

    def unidad_tiempo(símismo):
        raise NotImplementedError

    def obt_val_actual_var(símismo, var):
        return símismo.mod.obt_val_actual_var(var)

    def _iniciar_modelo(símismo, tiempo_final, nombre_corrida, vals_inic):
        from tinamit.EnvolturasMDS import generar_mds
        if símismo.mod is None or símismo.editado:
            símismo.publicar_modelo()
            símismo._estab_mod(generar_mds())
            símismo.editado = False

        símismo.mod.corrida_activa = nombre_corrida

        símismo.mod._iniciar_modelo(tiempo_final=tiempo_final, nombre_corrida=nombre_corrida, vals_inic=vals_inic)

    def _cambiar_vals_modelo_externo(símismo, valores):
        return símismo.mod._cambiar_vals_modelo_externo(valores=valores)

    def _incrementar(símismo, paso, guardar_cada=None):
        return símismo.mod._incrementar(paso=paso, guardar_cada=guardar_cada)

    def _leer_vals(símismo):
        return símismo.mod._leer_vals()

    def cerrar_modelo(símismo):
        return símismo.mod.cerrar_modelo()

    def leer_arch_resultados(símismo, archivo, var=None, col_tiempo='tiempo'):
        return símismo.mod.leer_arch_resultados(archivo=archivo, var=var)

    def publicar_modelo(símismo):
        raise NotImplementedError

    def paralelizable(símismo):
        return símismo.mod.paralelizable()
