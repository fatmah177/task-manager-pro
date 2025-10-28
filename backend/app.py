# app.py hallo 
# ===============================
# Diese Datei startet den Flask-Webserver und definiert "Routen" (URLs),
# die dein Browser aufrufen kann. Jede Route liefert eine Antwort zurück.
# Wir definieren:
#   - "/"        → einfacher Test, um zu sehen, dass der Server läuft
#   - "/tasks"   → liefert eine Liste von Aufgaben (als JSON)

from flask import Flask, jsonify, request   # Flask = Web-Framework; jsonify = macht JSON-Antworten
from models import User, Day, Task  # jetzt auch User und Day importieren!

# Wir erzeugen eine Flask-App-Instanz. Das ist dein Webserver.

app = Flask(__name__) #Hier erstellst du deine Web-App (das Herz deiner Anwendung).
                      #app ist eine Variable, in der deine Flask-Anwendung gespeichert wird.
                      #Flask(__name__) ist ein Konstruktor — er erstellt ein neues Flask-Objekt.

# ===============================
# "Datenbanken" (vorläufig in Speicher-Listen)
# ===============================
users = []  # Liste aller Benutzer
days = []   # Liste aller Tage
tasks = []  # Liste aller Aufgaben                      

# -----------------------------
# 1) Beispiel-Daten (in-memory)
# -----------------------------
# Für den Anfang speichern wir Aufgaben nur im Arbeitsspeicher (in einer Python-Liste).
# Später (nächster Schritt) ersetzen wir das durch eine richtige Datenbank (SQLite).
tasks = [
    Task(1, "Bericht schreiben", "Monatsbericht für den Chef erstellen", "In Progress"),
    Task(2, "Präsentation vorbereiten", "Folien für Meeting am Montag", "To Do"),
    Task(3, "Code überprüfen", "Backend testen und Kommentare ergänzen", "Done")
]


# -----------------------------
# 2) Route: Startseite ("/")
# -----------------------------
# Diese Route ist nur zum Testen, ob der Server läuft.
# Wenn du im Browser http://127.0.0.1:5000/ öffnest, solltest du den Text unten sehen.
@app.route("/") #Das ist ein sogenannter Decorator in Python (also ein Zusatz, der Funktionen steuert).
                #@app.route("/") sagt Flask:
                #„Wenn jemand im Browser die URL / öffnet, dann führe die folgende Funktion aus.“
def home():
    # Rückgabe ist einfacher Text (kein JSON)
    return "Backend funktioniert ✅ (Flask läuft!)"

# -----------------------------
# 3) Route: /tasks (GET)
# -----------------------------
# Diese Route gibt die Aufgabenliste als JSON zurück.
# GET bedeutet: Daten vom Server holen (lesen).
@app.route("/tasks", methods=["GET"])#„Wenn jemand im Browser zu /tasks geht,
                                     #dann führe bitte die Funktion get_tasks() aus.“
                                     #Wenn du schreibst: 👉 http://127.0.0.1:5000/tasks
                                     #Flask erkennt: „Ah! Das ist die Seite /tasks“
                                     #Flask startet die Funktion unten 👇
def get_tasks():
    """
    1) Wir nehmen die Python-Liste 'tasks'
    2) Wandeln jedes Task-Objekt mit to_json() in ein Dictionary um
    3) jsonify() macht daraus eine echte JSON-Antwort für den Browser
    """
    task_list = [task.to_json() for task in tasks] #Diese Zeile ist der Kern:
                                                   #Hier bereitest du die Daten vor, die du an den Browser schicken willst.
    
    return jsonify(task_list), 200   #„Okay, ich habe die Aufgabenliste fertig,
                                     #ich schicke sie an den Browser zurück."
                                     #jsonify(task_list) → wandelt deine Liste in JSON um
                                     #(das ist ein Format, das alle Webbrowser verstehen).
                                     #200 → bedeutet alles ist gut, kein Fehler (200 = Erfolgscode).
    
    """Wenn du /tasks aufrufst, zeigt Flask dir alle Aufgaben in einer Form, die dein Browser lesen 
       kann (JSON)."""



#------------------------------
# 4) Route: /tasks (POST)
# -----------------------------
# Diese Route erlaubt es, neue Aufgaben hinzuzufügen.
# Wir schicken JSON-Daten vom Client an den Server.
@app.route("/tasks", methods=["POST"])
def add_task():
    """
    1) request.get_json() liest die Daten, die der Benutzer schickt
    2) Wir holen Titel, Beschreibung und Status aus dem JSON
    3) Wir erstellen eine neue Task und hängen sie an die Liste
    """
    data = request.get_json()

    # Falls die Daten leer sind
    if not data:
        return jsonify({"error": "Keine Daten empfangen"}), 400

    # Felder aus dem JSON holen
    title = data.get("title")
    description = data.get("description")
    status = data.get("status", "To Do")

    # Neue ID berechnen (letzte ID + 1)
    new_id = tasks[-1].id + 1 if tasks else 1

    # Neue Aufgabe erzeugen
    new_task = Task(new_id, title, description, status)
    tasks.append(new_task)

    # Erfolgsmeldung zurückgeben
    return jsonify({"message": "Aufgabe hinzugefügt!", "task": new_task.to_json()}), 201

#das was soll ich in terminal schreiben:
"""
$body = @{
  title = "Neue Aufgabe"
  description = "Test per POST"
  status = "To Do"
} | ConvertTo-Json

Invoke-RestMethod -Method POST `
  -Uri http://127.0.0.1:5000/tasks `
  -ContentType "application/json" `
  -Body $body
  """

# -----------------------------
# 5) Route: /tasks/<id> (DELETE)
# -----------------------------
# Diese Route löscht eine bestimmte Aufgabe aus der Aufgabenliste.
# <int:task_id> bedeutet: Flask erwartet eine Zahl (ID) in der URL.
# Beispiel: Wenn du im Browser /tasks/3 eingibst, ist task_id = 3.
@app.route("/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    """
    Funktion, um eine Aufgabe zu löschen.
    Parameter:
        task_id (int): die ID der Aufgabe, die gelöscht werden soll.
    """

    # Wir sagen Flask, dass wir auf die globale Variable 'tasks' zugreifen wollen,
    # die oben in deinem Code definiert ist (die Liste mit allen Aufgaben).
    global tasks

    # Schritt 1: Wir suchen in der Liste 'tasks' nach einer Aufgabe mit der passenden ID.
    #   next(...) → gibt das erste Element zurück, das zur Bedingung passt.
    #   (t for t in tasks if t.id == task_id) → Generator, der alle Tasks überprüft.
    # Wenn keine passende Aufgabe gefunden wird, liefert next(..., None) den Wert None.
    task_to_delete = next((t for t in tasks if t.id == task_id), None)

    # Schritt 2: Wenn die Aufgabe nicht existiert, geben wir eine Fehlermeldung zurück.
    # jsonify(...) → wandelt ein Dictionary in eine JSON-Antwort für den Browser um.
    # HTTP-Statuscode 404 = "Not Found" (nicht gefunden)
    if task_to_delete is None:
        return jsonify({
            "error": f"Task mit ID {task_id} wurde nicht gefunden"
        }), 404

    # Schritt 3: Wenn die Aufgabe existiert, erstellen wir eine neue Liste,
    # die alle Tasks enthält, außer die mit der ID, die gelöscht werden soll.
    #   [t for t in tasks if t.id != task_id]
    # Das nennt man "List Comprehension" – eine elegante Art, Listen zu filtern.
    tasks = [t for t in tasks if t.id != task_id]

    # Schritt 4: Wir geben eine Erfolgsmeldung zurück.
    # jsonify(...) → damit der Browser / Client (z. B. PowerShell oder Postman)
    # eine schön formatierte JSON-Antwort bekommt.
    # HTTP-Statuscode 200 = "OK" (alles in Ordnung)
    return jsonify({
        "message": f"Task mit ID {task_id} erfolgreich gelöscht"
    }), 200
 
# das was soll ich in Terminal schreiben:
"""
Invoke-RestMethod -Method DELETE -Uri http://127.0.0.1:5000/tasks/4
"""



# -----------------------------
# 6) Route: /tasks/<id> (PUT)
# -----------------------------
# Diese Route erlaubt es, eine vorhandene Aufgabe zu AKTUALISIEREN.
# Das bedeutet: wir können z. B. den Titel, die Beschreibung oder den Status ändern.
# <int:task_id> → steht für die ID der Aufgabe, die geändert werden soll.
@app.route("/tasks/<int:task_id>", methods=["PUT"])
def update_task(task_id):
    """
    Funktion zum Aktualisieren (Bearbeiten) einer bestehenden Aufgabe.

    Beispiel:
        Wenn der Benutzer z. B. ID=2 ändern möchte,
        ruft er /tasks/2 mit der Methode PUT auf
        und sendet im Body ein JSON mit den neuen Daten.
    """

    # -------------------------------------
    # 1) JSON-Daten aus der Anfrage auslesen
    # -------------------------------------
    # request.get_json() → liest den JSON-Text, den der Benutzer geschickt hat,
    # und wandelt ihn in ein Python-Dictionary um.
    # Beispiel:
    #   {
    #     "title": "Neuer Titel",
    #     "status": "Done"
    #   }
    data = request.get_json()

    # Wenn keine Daten gesendet wurden (z. B. leere Anfrage):
    if not data:
        return jsonify({"error": "Keine Daten empfangen"}), 400

    # -------------------------------------
    # 2) Aufgabe in unserer Liste finden
    # -------------------------------------
    # Wir durchsuchen die globale Liste "tasks" nach der Aufgabe mit der passenden ID.
    #   next((t for t in tasks if t.id == task_id), None)
    # → sucht in tasks nach dem ersten Element, bei dem t.id == task_id.
    # → Wenn nichts gefunden wird, gibt es None zurück.
    task = next((t for t in tasks if t.id == task_id), None)

    # Wenn keine passende Aufgabe existiert, geben wir einen Fehler zurück.
    if task is None:
        return jsonify({"error": f"Task mit ID {task_id} wurde nicht gefunden"}), 404

    # -------------------------------------
    # 3) Felder aktualisieren (Teil-Update)
    # -------------------------------------
    # Wir prüfen, welche Felder im JSON enthalten sind.
    # Nur die gesendeten Felder werden geändert,
    # die anderen bleiben unverändert.
    if "title" in data:
        # Das neue Feld 'title' überschreibt den alten Wert
        task.title = data["title"]

    if "description" in data:
        # Das neue Feld 'description' überschreibt den alten Wert
        task.description = data["description"]

    if "status" in data:
        # Das neue Feld 'status' überschreibt den alten Wert
        task.status = data["status"]

    # -------------------------------------
    # 4) Antwort zurückgeben
    # -------------------------------------
    # jsonify() → wandelt das Dictionary in JSON um,
    # damit der Browser / Client (PowerShell, Postman, etc.) es lesen kann.
    # Wir geben auch die aktualisierte Aufgabe zurück, damit der Benutzer sehen kann,
    # was sich geändert hat.
    return jsonify({
        "message": "Task erfolgreich aktualisiert!",
        "task": task.to_json()
    }), 200

# das was soll ich in Terminal schreiben
"""
$update = @{
  title = "Praesentation fertig"   # kein ä
  status = "Done"
} | ConvertTo-Json

Invoke-RestMethod -Method PUT `
  -Uri http://127.0.0.1:5000/tasks/2 `
  -ContentType "application/json" `
  -Body $update
"""


# ================================================================
# AB HIER: NEUE ROUTEN (Schritt 3–7) – MIT KOMMENTAREN ZU JEDER ZEILE
# ================================================================

# WICHTIG: Ganz oben in der Datei musst du sicherstellen, dass dieser Import vorhanden ist:
# from models import User, Day, Task
# (Falls du den schon hast, NICHT doppelt einfügen!)

# Außerdem brauchst du (einmal weit oben) diese drei Listen als "Mini-Datenbank":
# users = []   # alle Benutzer
# days  = []   # alle Kalendertage
# tasks = []   # alle Aufgaben (hast du schon – NICHT doppelt anlegen!)


# ---------------------------------------------------------------
# 3) Benutzer anlegen: POST /users
# ---------------------------------------------------------------
@app.route("/users", methods=["POST"])  # Definiert eine neue Route /users, die NUR POST-Anfragen akzeptiert
def create_user():                      # Funktionsname ist frei wählbar; Flask ruft sie auf, wenn /users per POST kommt
    """
    Erwartet JSON-Daten vom Client, z. B.:
        { "username": "ouissal", "password": "1234" }
    Erstellt daraus einen neuen Benutzer und speichert ihn in der Liste 'users'.
    """
    data = request.get_json()          # Liest den JSON-Body der Anfrage und wandelt ihn in ein Python-Dict um

    username = data.get("username")    # Holt den Wert zu "username" aus dem JSON (oder None, wenn nicht vorhanden)
    password = data.get("password")    # Holt den Wert zu "password"

    if not username or not password:   # Validierung: Beide Felder müssen vorhanden und nicht leer sein
        return jsonify({               # Falls ungültig: Fehlermeldung als JSON zurückgeben …
            "error": "username und password sind Pflichtfelder"
        }), 400                        # … mit HTTP-Status 400 (Bad Request)

    # Prüfen, ob es den Benutzernamen schon gibt (einfacher Duplikat-Check in der Liste)
    if any(u.username == username for u in users):
        return jsonify({"error": "Benutzername existiert bereits"}), 400

    new_id = len(users) + 1            # Einfache ID-Vergabe: Anzahl existierender Benutzer + 1
    new_user = User(new_id, username, password)  # Erzeugt ein neues User-Objekt

    users.append(new_user)             # Speichert den neuen Benutzer in unserer "Mini-Datenbank" (Liste)

    return jsonify({                   # Antwort als JSON: Bestätigung + Benutzer (ohne Passwort)
        "message": "Benutzer erfolgreich erstellt",
        "user": new_user.to_json()     # to_json() gibt nur sichere Felder zurück (z. B. kein Passwort)
    }), 201                            # HTTP-Status 201 = Created (Ressource erzeugt)


# ---------------------------------------------------------------
# 4) Benutzer anzeigen: GET /users
# ---------------------------------------------------------------
@app.route("/users", methods=["GET"])   # Definiert Route /users für GET-Anfragen (Liste aller Benutzer)
def get_users():
    # Wandelt jeden Benutzer mit to_json() in ein Dict um und gibt eine Liste zurück
    return jsonify([u.to_json() for u in users]), 200  # 200 = OK

 #das was soll ich in Terminal schreiben
"""
$u = @{ username = "ouissal"; password = "1234" } | ConvertTo-Json
Invoke-RestMethod -Method POST -Uri http://127.0.0.1:5000/users -ContentType "application/json" -Body $u
"""


# ---------------------------------------------------------------
# 5) Neuen Kalendertag anlegen: POST /days
# ---------------------------------------------------------------
@app.route("/days", methods=["POST"])   # Definiert Route /days, akzeptiert POST (neuen Tag anlegen
def create_day():
    """
    Erwartet JSON wie:
        { "date": "2025-10-28" }
    Legt einen neuen 'Day' an und speichert ihn in 'days'.
    """
    data = request.get_json()          # JSON-Body einlesen
    date_value = data.get("date")      # Datum als String im ISO-Format, z. B. "2025-10-28"

    if not date_value:                 # Validierung: Datum muss übergeben werden
        return jsonify({"error": "Datum ist erforderlich"}), 400

    new_id = len(days) + 1             # Einfache ID-Vergabe für Tage
    new_day = Day(new_id, date_value)  # Erzeugt neues Day-Objekt (mit leerer tasks-Liste)

    days.append(new_day)               # Speichern in unserer "Mini-Datenbank" (Liste)

    return jsonify({                   # JSON-Antwort mit Bestätigung und dem neuen Tag
        "message": "Neuer Tag erstellt",
        "day": new_day.to_json()
    }), 201


# ---------------------------------------------------------------
# 6) Alle Kalendertage anzeigen: GET /days
# ---------------------------------------------------------------
@app.route("/days", methods=["GET"])    # Definiert Route /days für GET-Anfragen (Liste aller Tage)
def get_days():
    # Gibt ALLE Days zurück; jeder Day enthält seine tasks bereits als Liste (siehe Day.to_json())
    return jsonify([d.to_json() for d in days]), 200

 # das was soll ich in Terminal schreiben
""" 
$d = @{ date = "2025-10-28" } | ConvertTo-Json
Invoke-RestMethod -Method POST -Uri http://127.0.0.1:5000/days -ContentType "application/json" -Body $d
"""


# ---------------------------------------------------------------
# 7) Aufgabe einem bestimmten Tag hinzufügen: POST /days/<id>/tasks
# ---------------------------------------------------------------
@app.route("/days/<int:day_id>/tasks", methods=["POST"])  # Route mit Pfad-Parameter <int:day_id> (muss eine Zahl sein)
def add_task_to_day(day_id):
    """
    Hängt eine neue Aufgabe an den Tag mit der ID 'day_id'.
    Erwarteter JSON-Body:
        {
          "title": "Python lernen",
          "description": "Flask API weiterbauen",
          "status": "To Do",          # optional (Standard: "To Do")
          "user_id": 1                # optional: Zuordnung zu einem Benutzer
        }
    """
    # 1) Tag suchen, zu dem die Aufgabe hinzugefügt werden soll
    day = next((d for d in days if d.id == day_id), None)  # Sucht in der Liste 'days' den Tag mit passender ID
    if not day:                                            # Wenn nicht gefunden:
        return jsonify({"error": f"Tag mit ID {day_id} wurde nicht gefunden"}), 404  # 404 = Not Found

    # 2) Daten der neuen Aufgabe einlesen
    data = request.get_json()           # JSON-Body in Dict umwandeln
    title = data.get("title")           # Pflichtfeld: Kurzer Titel der Aufgabe
    description = data.get("description")  # Pflichtfeld: Beschreibung/Details
    status = data.get("status", "To Do")   # Optional: Status, Standard "To Do"
    user_id = data.get("user_id")          # Optional: Zuordnung zu einem Benutzer (ID)

    # 3) Pflichtfelder prüfen
    if not title or not description:    # Wenn Titel oder Beschreibung fehlen:
        return jsonify({"error": "title und description sind Pflichtfelder"}), 400  # 400 = Bad Request

    # 4) Neue Aufgaben-ID vergeben
    new_id = len(tasks) + 1             # Einfache ID-Vergabe basierend auf Gesamtzahl der Aufgaben

    # 5) Task-Objekt erzeugen (inkl. Zuordnung zu user_id und day_id)
    new_task = Task(new_id, title, description, status, user_id, day_id)

    # 6) In globaler Liste speichern (damit wir alle Aufgaben zentral haben)
    tasks.append(new_task)

    # 7) UND auch am gewünschten Tag „anhängen“, damit der Tag seine Aufgaben kennt
    day.add_task(new_task)

    # 8) JSON-Antwort mit Bestätigung und neuem Task-Objekt
    return jsonify({
        "message": f"Task wurde zum Tag {day_id} hinzugefügt",
        "task": new_task.to_json()
    }), 201  # 201 = Created
       


# Das hier startet den Server im "Entwicklermodus" (debug=True).
# Du startest ihn in der Konsole mit:  python app.py
if __name__ == "__main__":
    app.run(debug=True) #Das ist der Befehl, der deine Web-App wirklich startet 🚀
                        #Ohne diese Zeile passiert nichts — Flask würde einfach still dastehen.
