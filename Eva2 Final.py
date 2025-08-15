import sqlite3
import csv
import datetime

DB_NAME = "MovimientosYCtaCte.db"


def crear_conexion():
    """Crea y retorna una conexión a la base de datos SQLite."""
    return sqlite3.connect(DB_NAME)


def crear_tablas():
    """
    Crea las tablas ctacte y movimientos según la nueva especificación.
    - ctacte: almacena información de la cuenta corriente.
    - movimientos: almacena movimientos asociados a cada cuenta.
    """
    with crear_conexion() as con:
        cursor = con.cursor()

        # Crear tabla ctacte
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ctacte (
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                NumeroCtaCte REAL NOT NULL,
                rutTitularCta TEXT NOT NULL CHECK(length(rutTitularCta) <= 12),
                nomTitularCta TEXT NOT NULL CHECK(length(nomTitularCta) <= 105),
                SaldoCta REAL NOT NULL DEFAULT 0.0
            )
        ''')

        # Crear tabla movimientos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS movimientos (
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                idCtaCte INTEGER NOT NULL,
                idMovimientos REAL NOT NULL,
                tipoMovimiento INTEGER NOT NULL CHECK(tipoMovimiento IN (0,1)),
                Monto REAL NOT NULL,
                FOREIGN KEY (idCtaCte) REFERENCES ctacte(ID) ON DELETE CASCADE
            )
        ''')


# Llamada inicial para crear tablas
crear_tablas()


class CuentaCorriente:
    """
    Representa una cuenta corriente con operaciones de depósito y retiro.
    """

    def __init__(self, numero_cuenta, rut_titular, nombre_titular, saldo_inicial=0.0):
        self.numero_cuenta = numero_cuenta
        self.rut_titular = rut_titular
        self.nombre_titular = nombre_titular
        self.saldo = saldo_inicial
        self.id = self._registrar_en_bd()

    def _registrar_en_bd(self):
        """Registra la cuenta en la base de datos y devuelve su ID."""
        with crear_conexion() as con:
            cursor = con.cursor()
            cursor.execute('''
                INSERT INTO ctacte (NumeroCtaCte, rutTitularCta, nomTitularCta, SaldoCta)
                VALUES (?, ?, ?, ?)
            ''', (self.numero_cuenta, self.rut_titular, self.nombre_titular, self.saldo))
            return cursor.lastrowid

    def depositar(self, monto, id_movimiento):
        """Realiza un depósito en la cuenta."""
        if monto <= 0:
            raise ValueError("El monto a depositar debe ser positivo.")
        self.saldo += monto
        self._actualizar_saldo_bd()
        self._registrar_movimiento(id_movimiento, 1, monto)

    def retirar(self, monto, id_movimiento):
        """Realiza un retiro de la cuenta."""
        if monto <= 0:
            raise ValueError("El monto a retirar debe ser positivo.")
        if monto > self.saldo:
            raise ValueError("Saldo insuficiente.")
        self.saldo -= monto
        self._actualizar_saldo_bd()
        self._registrar_movimiento(id_movimiento, 0, monto)

    def _actualizar_saldo_bd(self):
        """Actualiza el saldo en la base de datos."""
        with crear_conexion() as con:
            cursor = con.cursor()
            cursor.execute(
                'UPDATE ctacte SET SaldoCta = ? WHERE ID = ?',
                (self.saldo, self.id)
            )

    def _registrar_movimiento(self, id_movimiento, tipo, monto):
        """Registra un movimiento asociado a esta cuenta."""
        with crear_conexion() as con:
            cursor = con.cursor()
            cursor.execute('''
                INSERT INTO movimientos (idCtaCte, idMovimientos, tipoMovimiento, Monto)
                VALUES (?, ?, ?, ?)
            ''', (self.id, id_movimiento, tipo, monto))

    @staticmethod
    def exportar_cuentas_csv(nombre_archivo='CuentasCorrientes.csv'):
        """Exporta todas las cuentas a un archivo CSV."""
        with crear_conexion() as con:
            cursor = con.cursor()
            cursor.execute("SELECT * FROM ctacte")
            resultados = cursor.fetchall()
            columnas = [desc[0] for desc in cursor.description]

        with open(nombre_archivo, 'w', newline='', encoding='utf-8') as archivo:
            escritor = csv.writer(archivo)
            escritor.writerow(columnas)
            escritor.writerows(resultados)
        print(f"Se exportaron {len(resultados)} cuentas a {nombre_archivo}.")

    @staticmethod
    def exportar_movimientos_csv(nombre_archivo='Movimientos.csv'):
        """Exporta todos los movimientos a un archivo CSV."""
        with crear_conexion() as con:
            cursor = con.cursor()
            cursor.execute("SELECT * FROM movimientos")
            resultados = cursor.fetchall()
            columnas = [desc[0] for desc in cursor.description]

        with open(nombre_archivo, 'w', newline='', encoding='utf-8') as archivo:
            escritor = csv.writer(archivo)
            escritor.writerow(columnas)
            escritor.writerows(resultados)
        print(f"Se exportaron {len(resultados)} movimientos a {nombre_archivo}.")


# ====== EJEMPLO DE USO ======
if __name__ == "__main__":
    cuenta1 = CuentaCorriente(1001, "12.345.678-9", "Juan Pérez", 150000)
    cuenta1.depositar(20000, 1)
    cuenta1.retirar(5000, 2)

    cuenta2 = CuentaCorriente(1002, "98.765.432-1", "María López", 300000)
    cuenta2.depositar(50000, 3)

    CuentaCorriente.exportar_cuentas_csv()
    CuentaCorriente.exportar_movimientos_csv()