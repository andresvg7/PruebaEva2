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
            NumeroCtaCte NUMERIC NOT NULL,
            rutTitularCta TEXT NOT NULL,
            nomTitularCta TEXT NOT NULL,
            SaldoCta NUMERIC NOT NULL DEFAULT 0.0
        )
    ''')

    # Tabla Movimientos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Movimientos (
            IdMovimientos INTEGER PRIMARY KEY AUTOINCREMENT,
            idCtaCte INTEGER NOT NULL,
            tipoMovimiento INTEGER NOT NULL, -- 0 = Abono, 1 = Carga
            Monto NUMERIC NOT NULL,
            FOREIGN KEY (idCtaCte) REFERENCES CtaCte(ID)
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
    """

    def __init__(self, numero_cuenta, rut, nombre, saldo_inicial=0.0):
        self.NumeroCtaCte = numero_cuenta
        self.rutTitularCta = rut
        self.nomTitularCta = nombre
        self.SaldoCta = saldo_inicial
        self.ID = self._registrar_en_bd()

    def _registrar_en_bd(self):
        """Registra la cuenta en la base de datos."""
        con = crear_conexion()
        query = f"""
            INSERT INTO CtaCte (NumeroCtaCte, rutTitularCta, nomTitularCta, SaldoCta)
            VALUES ({self.NumeroCtaCte}, '{self.rutTitularCta}', '{self.nomTitularCta}', {self.SaldoCta})
        """
        objCursor = con.cursor()
        objCursor.execute(query)
        con.commit()

        # Recuperar ID de la cuenta usando SELECT
        objCursor.execute(f"SELECT ID FROM CtaCte WHERE NumeroCtaCte={self.NumeroCtaCte} AND rutTitularCta='{self.rutTitularCta}'")
        ID_cuenta = objCursor.fetchone()[0]

        con.close()
        return ID_cuenta

    # ==============================
    # Operaciones
    # ==============================
    def abonar(self, monto):
        """Abona un monto positivo a la cuenta."""
        if monto <= 0:
            print("El monto debe ser mayor a 0.")
            return
        self.SaldoCta += monto
        self._actualizar_saldo_bd()
        self._registrar_movimiento(monto, 0)

    def cargar(self, monto):
        """Carga un monto positivo a la cuenta, verificando saldo suficiente."""
        if monto <= 0:
            print("El monto debe ser mayor a 0.")
            return
        if self.SaldoCta < monto:
            print("Saldo insuficiente para realizar la operación.")
            return
        self.SaldoCta -= monto
        self._actualizar_saldo_bd()
        self._registrar_movimiento(monto, 1)

    def _actualizar_saldo_bd(self):
        """Actualiza el saldo de la cuenta en la base de datos."""
        con = crear_conexion()
        query = f"UPDATE CtaCte SET SaldoCta={self.SaldoCta} WHERE ID={self.ID}"
        objCursor = con.cursor()
        objCursor.execute(query)
        con.commit()
        con.close()

    def _registrar_movimiento(self, monto, tipo):
        """
        Registra un movimiento en la base de datos usando query tipo string.
        Args:
            monto (float): Monto del movimiento.
            tipo (int): 0 = Abono, 1 = Carga.
        """
        con = crear_conexion()
        query = f"""
            INSERT INTO Movimientos (idCtaCte, tipoMovimiento, Monto)
            VALUES ({self.ID}, {tipo}, {monto})
        """
        objCursor = con.cursor()
        objCursor.execute(query)
        con.commit()
        con.close()

    # ==============================
    # Exportar a CSV
    # ==============================
    def exportar_csv_ctacte(self):
        """Exporta todas las cuentas a CSV."""
        con = crear_conexion()
        cursor = con.cursor()
        cursor.execute("SELECT * FROM CtaCte")
        cuentas = cursor.fetchall()
        with open('CuentasCorrientes.csv', 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(["ID Cta Cte", "Numero Cta Cte", "Rut Titular", "Nombre Titular", "Saldo"])
            for ID, numero, rut, nombre, saldo in cuentas:
                writer.writerow([ID, numero, rut, nombre, saldo])
        con.close()
        print("Exportación de Cuentas Corrientes completa.")

    def exportar_csv_movimientos(self):
        """Exporta todos los movimientos a CSV."""
        con = crear_conexion()
        cursor = con.cursor()
        cursor.execute("SELECT IdMovimientos, idCtaCte, tipoMovimiento, Monto FROM Movimientos")
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