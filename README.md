# Integrare RER Group pentru Home Assistant (RETIM, REBU, RER)

Această integrare personalizată permite monitorizarea conturilor de salubritate de la diversele filiale ale grupului RER din România direct în interfața Home Assistant.

## Versiune curentă: 1.0.1

---

## 🚀 Facilități
* **Sold Total de Plată**: Calculează automat suma datorată din toate facturile neachitate (folosind câmpul `dueAmount` din API).
* **Detalii Facturare**: Senzori pentru numărul facturii, data emiterii și data scadenței pentru cea mai recentă factură.
* **Informații Client**: Date despre contract și locația de consum (afișate ca senzori de Diagnostic).
* **Suport Multi-Portal**: Selectarea furnizorului dorit (RETIM, REBU, RER Vest, etc.) direct din interfața de configurare.
* **Grupare pe Dispozitiv**: Toate entitățile sunt organizate sub un singur "Device" pentru o gestiune ușoară.
* **Securitate**: Gestionare automată a token-urilor de autentificare (Bearer Token).

## 🏢 Furnizori Suportați
Integrarea este compatibilă cu platformele "Contul Meu" ale:
* **RETIM** (Timișoara și zona de Vest)
* **REBU** (București/Ilfov)
* **RER Vest** (Oradea)
* **RER Sud** (Buzău)
* **RER Brăila**
* **RER Galați**

---

## 🛠️ Instalare

### Metoda 1: HACS (Recomandat)
1. Deschide **HACS** în Home Assistant.
2. Click pe cele trei puncte din dreapta sus și selectează **Custom repositories**.
3. Adaugă URL-ul acestui depozit GitHub.
4. Selectează categoria **Integration**.
5. Click pe **Add**, apoi caută "RER Group" în lista HACS și descarcă-l.
6. **Repornește Home Assistant.**

### Metoda 2: Manual
1. Descarcă arhiva acestui depozit.
2. Copiază folderul `rer_group` în directorul `custom_components` al instalării tale Home Assistant.
3. **Repornește Home Assistant.**

---

## ⚙️ Configurare

1. Mergi la **Settings (Configurare)** > **Devices & Services (Dispozitive și Servicii)**.
2. Click pe butonul **Add Integration** din dreapta jos.
3. Caută **RER Group** în listă.
4. În fereastra de configurare:
   * Selectează **Service Provider** (ex: RETIM).
   * Introdu adresa de **E-mail** aferentă contului.
   * Introdu **Parola**.
5. Click pe **Submit**.

---

## 📊 Detalii Tehnice
* **Interval de Actualizare**: Datele sunt verificate la fiecare **3 ore**.
* **Calcul Sold**: Senzorul de sold însumează toate intrările din lista de facturi care au parametrul `"unpaid": true`.
* **Diagnostic**: Datele de profil (telefon, email, adresa contract) sunt marcate ca entități de diagnostic pentru a nu polua interfața principală.

## ⚠️ Depanare
Dacă senzorii nu apar sau datele nu se actualizează:
1. Verifică log-urile Home Assistant (**Settings > System > Logs**).
2. Asigură-te că poți accesa portalul web al furnizorului cu aceleași date de autentificare.
3. Dacă primești eroarea `invalid_auth`, verifică dacă ai selectat furnizorul corect în pasul de configurare.

---

## 📝 Licență
Acest proiect este dezvoltat în scop personal. Nu este o aplicație oficială a grupului RER sau RETIM.