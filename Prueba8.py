import sqlite3
import csv

# ==============================
# Conexión a la base de datos
# ==============================
def crear_conexion():
    """Crea y retorna una conexión a la base de datos."""
    return sqlite3.connect("MovimentosYCtaCte.db")


# ==============================
# Creación de tablas
# ==============================
def crear_tablas():
    """
    Crea las tablas 'CtaCte' y 'Movimientos' si no existen.
    """
    con = crear_conexion()
    cursor = con.cursor()

    # Tabla CtaCte
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS CtaCte (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            numero_cta_cte NUMERIC NOT NULL,
            rut_titular_cta TEXT NOT NULL,
            nombre_titular_cta TEXT NOT NULL,
            saldo_cta NUMERIC NOT NULL DEFAULT 0.0
        )
    ''')

    # Tabla Movimientos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Movimientos (
            id_movimientos INTEGER PRIMARY KEY AUTOINCREMENT,
            id_cta_cte INTEGER NOT NULL,
            tipo_movimiento INTEGER NOT NULL, -- 0 = Abono, 1 = Carga
            monto NUMERIC NOT NULL,
            FOREIGN KEY (id_cta_cte) REFERENCES CtaCte(ID)
        )
    ''')

    con.commit()
    con.close()

# Crear tablas al iniciar
crear_tablas()


# ==============================
# Clase CuentaCorriente
# ==============================
class CuentaCorriente:
    """
    Clase que representa una cuenta corriente bancaria.

    Atributos:
        numero_cta_cte (int): Número único de la cuenta corriente.
        rut_titular_cta (str): RUT del titular de la cuenta.
        nombre_titular_cta (str): Nombre del titular de la cuenta.
        saldo_cta (float): Saldo actual de la cuenta.
        id (int): Identificador único de la cuenta en la base de datos.
    """

    def __init__(self, numero_cta_cte, rut_titular_cta, nombre_titular_cta, saldo_inicial=0.0):
        """
        Constructor que inicializa una nueva cuenta corriente y la registra en la base de datos.

        Args:
            numero_cta_cte (int): Número único de la cuenta corriente.
            rut_titular_cta (str): RUT del titular de la cuenta.
            nombre_titular_cta (str): Nombre del titular de la cuenta.
            saldo_inicial (float): Saldo inicial de la cuenta. Por defecto es 0.0.
        """
        self.numero_cta_cte = numero_cta_cte
        self.rut_titular_cta = rut_titular_cta
        self.nombre_titular_cta = nombre_titular_cta
        self.saldo_cta = saldo_inicial
        self.id = self._registrar_en_bd()

    def _registrar_en_bd(self):
        """Registra la cuenta en la base de datos y retorna su ID."""
        con = crear_conexion()
        query = f"""
            INSERT INTO CtaCte (numero_cta_cte, rut_titular_cta, nombre_titular_cta, saldo_cta)
            VALUES ({self.numero_cta_cte}, '{self.rut_titular_cta}', '{self.nombre_titular_cta}', {self.saldo_cta})
        """
        cursor = con.cursor()
        cursor.execute(query)
        con.commit()

        # Recuperar ID de la cuenta usando SELECT
        cursor.execute(f"SELECT ID FROM CtaCte WHERE numero_cta_cte={self.numero_cta_cte} AND rut_titular_cta='{self.rut_titular_cta}'")
        id_cuenta = cursor.fetchone()[0]

        con.close()
        return id_cuenta

    # ==============================
    # Operaciones
    # ==============================
    def abonar(self, monto):
        """
        Abona un monto positivo a la cuenta.

        Args:
            monto (float): Monto a abonar.

        Returns:
            None
        """
        if monto <= 0:
            print("Error: El monto debe ser mayor a 0.")
            return
        self.saldo_cta += monto
        self._actualizar_saldo_bd()
        self._registrar_movimiento(monto, 0)
        print(f"Abono exitoso: ${monto:.2f} abonados a la cuenta {self.numero_cta_cte}. Saldo actual: ${self.saldo_cta:.2f}.")

    def cargar(self, monto):
        """
        Carga un monto positivo a la cuenta, verificando saldo suficiente.

        Args:
            monto (float): Monto a cargar.

        Returns:
            None
        """
        if monto <= 0:
            print("Error: El monto debe ser mayor a 0.")
            return
        if self.saldo_cta < monto:
            print(f"Error: Saldo insuficiente. Saldo actual: ${self.saldo_cta:.2f}.")
            return
        self.saldo_cta -= monto
        self._actualizar_saldo_bd()
        self._registrar_movimiento(monto, 1)
        print(f"Carga exitosa: ${monto:.2f} cargados de la cuenta {self.numero_cta_cte}. Saldo actual: ${self.saldo_cta:.2f}.")

    def _actualizar_saldo_bd(self):
        """Actualiza el saldo de la cuenta en la base de datos."""
        con = crear_conexion()
        query = f"UPDATE CtaCte SET saldo_cta={self.saldo_cta} WHERE ID={self.id}"
        cursor = con.cursor()
        cursor.execute(query)
        con.commit()
        con.close()

    def _registrar_movimiento(self, monto, tipo):
        """
        Registra un movimiento en la base de datos.

        Args:
            monto (float): Monto del movimiento.
            tipo (int): 0 = Abono, 1 = Carga.
        """
        con = crear_conexion()
        query = f"""
            INSERT INTO Movimientos (id_cta_cte, tipo_movimiento, monto)
            VALUES ({self.id}, {tipo}, {monto})
        """
        cursor = con.cursor()
        cursor.execute(query)
        con.commit()
        con.close()

    # ==============================
    # Exportar a CSV
    # ==============================
    def exportar_csv_ctacte(self):
        """Exporta todas las cuentas a un archivo CSV."""
        con = crear_conexion()
        cursor = con.cursor()
        cursor.execute("SELECT * FROM CtaCte")
        cuentas = cursor.fetchall()
        with open('CuentasCorrientes.csv', 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(["ID Cta Cte", "Numero Cta Cte", "Rut Titular", "Nombre Titular", "Saldo"])
            for id_cta, numero, rut, nombre, saldo in cuentas:
                writer.writerow([id_cta, numero, rut, nombre, saldo])
        con.close()
        print("Exportación de Cuentas Corrientes completa.")

    def exportar_csv_movimientos(self):
        """Exporta todos los movimientos a un archivo CSV."""
        con = crear_conexion()
        cursor = con.cursor()
        cursor.execute("SELECT id_movimientos, id_cta_cte, tipo_movimiento, monto FROM Movimientos")
        movimientos = cursor.fetchall()
        with open('Movimientos.csv', 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(["ID Movimiento", "ID Cta Cte", "Tipo Movimiento", "Monto", "Descripcion"])
            for id_mov, id_cta, tipo, monto in movimientos:
                descripcion = "Abono" if tipo == 0 else "Cargo"
                writer.writerow([id_mov, id_cta, tipo, monto, descripcion])
        con.close()
        print("Exportación de Movimientos completa.")

# ==============================
# Ejemplo de uso
# ==============================
cuenta1 = CuentaCorriente(10000001, "12345678-9", "Matias Delgado", 150000)
cuenta2 = CuentaCorriente(10000002, "98765432-1", "Danilo Lopez", 250000)
cuenta3 = CuentaCorriente(10000003, "11223344-5", "Samira Ortega", 50000)

cuenta3.abonar(20000)
cuenta1.cargar(5000)
cuenta2.abonar(30000)
cuenta1.cargar(999999)  # Error por saldo insuficiente
cuenta1.abonar(-100)     # Error por monto inválido

# Exportar a CSV
cuenta1.exportar_csv_ctacte()
cuenta1.exportar_csv_movimientos()