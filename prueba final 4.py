import sqlite3
import csv

def crear_conexion():
    """Crea y retorna una conexión a la base de datos."""
    return sqlite3.connect("MovimientosYCtaCte.db")

def crear_tablas():
    """Crea las tablas ctacte y movimientos si no existen, según nueva especificación."""
    con = crear_conexion()
    cursor = con.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ctacte (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            NumeroCtaCte DOUBLE NOT NULL,
            rutTitularCta VARCHAR(12) NOT NULL,
            nomTitularCta VARCHAR(105) NOT NULL,
            SaldoCta DOUBLE NOT NULL DEFAULT 0.0
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS movimientos (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            idCtaCte INTEGER NOT NULL,
            tipoMovimiento BIT NOT NULL, -- 0: Abono, 1: Cargo
            Monto DOUBLE NOT NULL,
            FOREIGN KEY (idCtaCte) REFERENCES ctacte(ID)
        )
    ''')

    con.commit()
    con.close()

# Crear tablas
crear_tablas()

class CuentaCorriente:
    """Clase que representa una cuenta corriente bancaria."""

    def __init__(self, numero_cta, rut_titular, nombre_titular, saldo_inicial=0.0):
        self.NumeroCtaCte = numero_cta
        self.rutTitularCta = rut_titular
        self.nomTitularCta = nombre_titular
        self.SaldoCta = saldo_inicial
        self.ID = self._registrar_en_bd()

    def _registrar_en_bd(self):
        con = crear_conexion()
        cursor = con.cursor()
        cursor.execute('''
            INSERT INTO ctacte (NumeroCtaCte, rutTitularCta, nomTitularCta, SaldoCta)
            VALUES (?, ?, ?, ?)
        ''', (self.NumeroCtaCte, self.rutTitularCta, self.nomTitularCta, self.SaldoCta))
        con.commit()
        cuenta_id = cursor.lastrowid
        con.close()
        return cuenta_id

    def abonar(self, monto):
        if monto <= 0:
            print(" El monto a abonar debe ser mayor a 0.")
            return
        self.SaldoCta += monto
        self._actualizar_saldo_bd()
        self._registrar_movimiento(monto, 0)

    def cargar(self, monto):
        if monto <= 0:
            print(" El monto a cargar debe ser mayor a 0.")
            return
        if monto > self.SaldoCta:
            print(" Saldo insuficiente para realizar el cargo.")
            return
        self.SaldoCta -= monto
        self._actualizar_saldo_bd()
        self._registrar_movimiento(monto, 1)

    def _actualizar_saldo_bd(self):
        con = crear_conexion()
        cursor = con.cursor()
        cursor.execute('UPDATE ctacte SET SaldoCta = ? WHERE ID = ?', (self.SaldoCta, self.ID))
        con.commit()
        con.close()

    def _registrar_movimiento(self, monto, tipo):
        con = crear_conexion()
        cursor = con.cursor()
        cursor.execute('''
            INSERT INTO movimientos (idCtaCte, tipoMovimiento, Monto)
            VALUES (?, ?, ?)
        ''', (self.ID, tipo, monto))
        con.commit()
        con.close()

    @staticmethod
    def exportar_ctas_csv():
        """Exporta todos los registros de ctacte a CSV con nombres claros."""
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
        print(" Exportación de cuentas completada correctamente.\n")

    @staticmethod
    def exportar_movimientos_csv():
        """Exporta todos los registros de movimientos a CSV con nombres claros."""
        con = crear_conexion()
        cursor = con.cursor()
        cursor.execute("SELECT * FROM movimientos")
        resultados = cursor.fetchall()
        columnas = [desc[0] for desc in cursor.description]

        with open('MovimientosCuentas.csv', 'w', newline='', encoding='utf-8') as archivo:
            escritor = csv.writer(archivo)
            escritor.writerow(columnas)
            for fila in resultados:
                escritor.writerow(fila)
        con.close()
        print(" Exportación de movimientos completada correctamente.\n")


# Ejemplo de uso
cuenta1 = CuentaCorriente(45214578, "17.985.747-1", "Alfredo Cardenas", 150000)
cuenta2 = CuentaCorriente(98563245, "9.222.874-2", "Danilo Ortega", 250000)

# Operaciones de prueba
cuenta1.abonar(50000)
cuenta1.cargar(20000)
cuenta1.cargar(999999)  # Error por saldo insuficiente
cuenta1.abonar(-100)  # Error por monto inválido


# Exportar datos
CuentaCorriente.exportar_ctas_csv()
CuentaCorriente.exportar_movimientos_csv()
