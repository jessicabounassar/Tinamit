from Conectado import Conectado


# Create a coupled model instance
modelo = Conectado()

# Establish SDM and Biofisical model paths. The Biofisical model path must point to the Python wrapper for the model.
modelo.estab_mds("C:\\Users\\you\\YourDocuments\\Azhar's model.vpm")

modelo.estab_bf('C:\\Users\\jmalar1\\Documents\\PycharmProjects\\Tinamit\\Ejemplos\\'
                'Ejemplo SAHYSMOD\\Envoltura SAHYSMOD.py')

# Couple models(Change variable names as needed)
modelo.conectar(var_mds="Groundwater Table", mds_fuente=False, var_bf="Groundwater Depth", conv=1)
modelo.conectar(var_mds="Groundwater Extraction", mds_fuente=True, var_bf="Groundwater Extraction", conv=1)
modelo.conectar(var_mds="Soil Salinity", var_bf="Soil Salinity", mds_fuente=False, conv=1)

# Simulate the coupled model
modelo.simular(paso=1, tiempo_final=12)