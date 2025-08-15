import sqlite3
import csv


def crear_conexion():
    """
    Crea y retorna una conexión a la base de datos SQLite.

    Returns:
        sqlite3.Connection: Objeto de conexión a la base de datos.
    """
    return sqlite3.connect("MovimientosYCtaCte.db")


def crear_tablas():
    """
    Crea las tablas 'ctacte' y 'movimientos' si no existen,
    siguiendo la nueva especificación de estructura.
    """
    con = crear_conexion()
    cursor = con.cursor()

    # Tabla de cuentas corrientes
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ctacte (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            NumeroCtaCte REAL NOT NULL,
            rutTitularCta TEXT NOT NULL,
            nomTitularCta TEXT NOT NULL,
            SaldoCta REAL NOT NULL DEFAULT 0.0
        )
    ''')

    # Tabla de movimientos (sin fecha)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS movimientos (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            idCtaCte INTEGER NOT NULL,
            tipoMovimiento INTEGER NOT NULL, -- 1 = Depósito, 0 = Retiro
            Monto REAL NOT NULL,
            FOREIGN KEY (idCtaCte) REFERENCES ctacte(ID)
        )
    ''')

    con.commit()
    con.close()


class CuentaCorriente:
    """
    Representa una cuenta corriente con operaciones de depósito y retiro.
    """

    def __init__(self, numero_cuenta, rut_titular, nombre_titular, saldo_inicial=0.0):
        """
        Inicializa una cuenta corriente y la registra en la base de datos.

        Args:
            numero_cuenta (float): Número único de la cuenta.
            rut_titular (str): RUT del titular.
            nombre_titular (str): Nombre del titular.
            saldo_inicial (float): Saldo inicial de la cuenta.
        """
        self.numero_cuenta = numero_cuenta
        self.rut_titular = rut_titular
        self.nombre_titular = nombre_titular
        self.saldo = saldo_inicial
        self.id = self._registrar_en_bd()

    def _registrar_en_bd(self):
        """Registra la cuenta en la tabla 'ctacte' y retorna su ID."""
        con = crear_conexion()
        cursor = con.cursor()
        cursor.execute('''
            INSERT INTO ctacte (NumeroCtaCte, rutTitularCta, nomTitularCta, SaldoCta)
            VALUES (?, ?, ?, ?)
        ''', (self.numero_cuenta, self.rut_titular, self.nombre_titular, self.saldo))
        con.commit()
        cuenta_id = cursor.lastrowid
        con.close()
        return cuenta_id

    def _actualizar_saldo_bd(self):
        """Actualiza el saldo en la base de datos."""
        con = crear_conexion()
        cursor = con.cursor()
        cursor.execute('UPDATE ctacte SET SaldoCta = ? WHERE ID = ?', (self.saldo, self.id))
        con.commit()
        con.close()

    def _registrar_movimiento(self, tipo, monto):
        """Registra un movimiento en la base de datos."""
        con = crear_conexion()
        cursor = con.cursor()
        cursor.execute('''
            INSERT INTO movimientos (idCtaCte, tipoMovimiento, Monto)
            VALUES (?, ?, ?)
        ''', (self.id, tipo, monto))
        con.commit()
        con.close()

    def abonar(self, monto):
        """
        Abona un monto a la cuenta si es válido.
        Muestra mensaje amigable en caso de error.
        """
        if monto <= 0:
            print("⚠ El monto a abonar debe ser mayor que 0.\n")
            return
        self.saldo += monto
        self._actualizar_saldo_bd()
        self._registrar_movimiento(1, monto)
        print(f"✅ Se abonaron ${monto:,.2f} a la cuenta {self.nombre_titular}. "
              f"Saldo actual: ${self.saldo:,.2f}\n")

    def cargar(self, monto):
        """
        Retira un monto de la cuenta si hay saldo suficiente.
        Muestra mensaje amigable en caso de error.
        """
        if monto <= 0:
            print("⚠ El monto a retirar debe ser mayor que 0.\n")
            return
        if monto > self.saldo:
            print(f"⚠ Saldo insuficiente. Saldo actual: ${self.saldo:,.2f}\n")
            return
        self.saldo -= monto
        self._actualizar_saldo_bd()
        self._registrar_movimiento(0, monto)
        print(f"✅ Se retiraron ${monto:,.2f} de la cuenta {self.nombre_titular}. "
              f"Saldo actual: ${self.saldo:,.2f}\n")

    @staticmethod
    def exportar_csv():
        """
        Exporta todas las cuentas a un archivo CSV con nombres semánticos.
        """
        con = crear_conexion()
        cursor = con.cursor()
        cursor.execute("SELECT * FROM ctacte")
        resultados = cursor.fetchall()
        columnas = [desc[0] for desc in cursor.description]

        with open('CuentasCorrientes.csv', 'w', newline='', encoding='utf-8') as archivo:
            escritor = csv.writer(archivo)
            escritor.writerow(columnas)
            for fila in resultados:
                escritor.writerow(fila)

        con.close()
        print("📄 Exportación completada correctamente.\n")


# --- Inicialización de la BD y pruebas ---
crear_tablas()

# Ejemplos de creación de cuentas
cuenta1 = CuentaCorriente(1001, "11.111.111-1", "Juan Perez", 150000)
cuenta2 = CuentaCorriente(1002, "22.222.222-2", "Maria Lopez", 250000)

# Operaciones de prueba
cuenta1.abonar(50000)
cuenta1.cargar(20000)
cuenta1.cargar(999999)  # Error por saldo insuficiente
cuenta1.abonar(-100)  # Error por monto inválido

# Exportación de datos
CuentaCorriente.exportar_csv()
