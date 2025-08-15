import sqlite3
import csv
import datetime

DB_NAME = "MovimientosYCtaCte.db"


def crear_conexion():
    """Crea y retorna una conexión a la base de datos."""
    return sqlite3.connect(DB_NAME)


def crear_tablas():
    """Crea las tablas CtaCte y Movimientos si no existen."""
    with crear_conexion() as con:
        cursor = con.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS CtaCte (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                titular TEXT NOT NULL,
                saldo REAL NOT NULL DEFAULT 0.0,
                fecha_apertura TEXT NOT NULL
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Movimientos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cuenta_id INTEGER NOT NULL,
                fecha TEXT NOT NULL,
                monto REAL NOT NULL,
                tipoMovimiento INTEGER NOT NULL, -- 0: Abono, 1: Cargo
                descripcion TEXT,
                FOREIGN KEY (cuenta_id) REFERENCES CtaCte(id)
            )
        ''')


# Llamar para crear las tablas
crear_tablas()


class CuentaCorriente:
    """
    Clase que representa una cuenta corriente bancaria.

    Atributos:
        titular (str): Nombre del titular de la cuenta.
        saldo (float): Saldo actual de la cuenta.
        id (int): Identificador único de la cuenta en la base de datos.
    """

    def __init__(self, titular, saldo_inicial=0.0):
        self.titular = titular
        self.saldo = saldo_inicial
        self.id = self._registrar_en_bd()

    def _registrar_en_bd(self):
        """Registra la cuenta en la base de datos y retorna su ID."""
        fecha = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with crear_conexion() as con:
            cursor = con.cursor()
            cursor.execute(
                'INSERT INTO CtaCte (titular, saldo, fecha_apertura) VALUES (?, ?, ?)',
                (self.titular, self.saldo, fecha)
            )
            return cursor.lastrowid

    def abonar(self, monto, descripcion=""):
        """
        Realiza un abono en la cuenta.

        Args:
            monto (float): Monto a abonar (debe ser positivo).
            descripcion (str): Descripción del movimiento.
        """
        if monto <= 0:
            raise ValueError("El monto a abonar debe ser mayor a cero.")
        self.saldo += monto
        self._actualizar_saldo_bd()
        self._registrar_movimiento(monto, 0, descripcion)

    def cargar(self, monto, descripcion=""):
        """
        Realiza un cargo en la cuenta.

        Args:
            monto (float): Monto a cargar (debe ser positivo y no superar el saldo).
            descripcion (str): Descripción del movimiento.
        """
        if monto <= 0:
            raise ValueError("El monto a cargar debe ser mayor a cero.")
        if monto > self.saldo:
            raise ValueError("Saldo insuficiente para realizar la operación.")
        self.saldo -= monto
        self._actualizar_saldo_bd()
        self._registrar_movimiento(monto, 1, descripcion)

    def _actualizar_saldo_bd(self):
        """Actualiza el saldo de la cuenta en la base de datos."""
        with crear_conexion() as con:
            cursor = con.cursor()
            cursor.execute('UPDATE CtaCte SET saldo = ? WHERE id = ?', (self.saldo, self.id))

    def _registrar_movimiento(self, monto, tipo, descripcion):
        """Registra un movimiento (abono o cargo) en la base de datos."""
        fecha = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with crear_conexion() as con:
            cursor = con.cursor()
            cursor.execute(
                'INSERT INTO Movimientos (cuenta_id, fecha, monto, tipoMovimiento, descripcion) '
                'VALUES (?, ?, ?, ?, ?)',
                (self.id, fecha, monto, tipo, descripcion)
            )

    @staticmethod
    def exportar_csv(nombre_archivo='CuentasCorrientes.csv'):
        """
        Exporta todos los registros de la tabla CtaCte a un archivo CSV.

        Args:
            nombre_archivo (str): Nombre del archivo CSV de salida.
        """
        try:
            with crear_conexion() as con:
                cursor = con.cursor()
                cursor.execute("SELECT * FROM CtaCte")
                resultados = cursor.fetchall()
                columnas = [desc[0] for desc in cursor.description]

            if not resultados:
                print("No hay cuentas para exportar.")
                return

            with open(nombre_archivo, 'w', newline='', encoding='utf-8') as archivo:
                escritor = csv.writer(archivo)
                escritor.writerow(columnas)
                for fila in resultados:
                    print(fila)
                    escritor.writerow(fila)

            print(f"Se exportaron {len(resultados)} cuentas correctamente a {nombre_archivo}.\n")

        except Exception as e:
            print(f"Error al exportar CSV: {e}")


# =======================
# EJEMPLO DE USO
# =======================
if __name__ == "__main__":
    # Instanciación de cuentas corrientes con valores de ejemplo
    cuenta1 = CuentaCorriente("Juan Pérez", 150000)
    cuenta2 = CuentaCorriente("María López", 250000)
    cuenta3 = CuentaCorriente("Carlos Díaz", 50000)
    cuenta4 = CuentaCorriente("Ana Torres", 100000)
    cuenta5 = CuentaCorriente("Luis Soto", 300000)
    cuenta6 = CuentaCorriente("Paula Rivas", 120000)

    # Realiza algunas operaciones para registrar movimientos
    cuenta3.abonar(20000, "Depósito sueldo")
    cuenta6.cargar(10000, "Pago servicios")
    cuenta5.abonar(50000, "Transferencia recibida")

    # Exporta los datos de cuentas corrientes a CSV
    CuentaCorriente.exportar_csv()