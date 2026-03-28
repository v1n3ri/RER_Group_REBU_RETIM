\# Integrare RER Group pentru Home Assistant



Această integrare personalizată permite monitorizarea conturilor de salubritate de la diversele filiale ale grupului RER din România (RETIM, REBU, RER Vest etc.) direct în interfața Home Assistant.



\## Furnizori Suportați

Această integrare funcționează cu portalurile "Contul Meu" pentru:

\* RETIM (Timișoara și zona de Vest)

\* REBU (București/Ilfov)

\* RER Vest (Oradea)

\* RER Sud (Buzău)

\* RER Brăila

\* RER Galați



\## Facilități

\* Sold Cont: Urmărește suma totală de plată (neachitată) în RON.

\* Detalii Ultima Factură: Creează automat senzori pentru numărul facturii, data emiterii și data scadenței.

\* Informații Profil: Senzori de diagnostic pentru detaliile contului (E-mail, Telefon, ID Contract).

\* Grupare pe Dispozitiv: Toate entitățile sunt organizate sub un singur "Dispozitiv" (Device) pentru o gestiune ușoară.

\* Reautentificare Automată: Gestionează expirarea sesiunilor fără a fi necesară intervenția manuală.



\---



\## Instalare



\### Instalare Manuală

1\. Descarcă codul sursă al integrării.

2\. Creează un folder numit "RER\_Group" în directorul "custom\_components" din instalarea ta Home Assistant.

3\. Copiază toate fișierele proiectului în folderul creat.

4\. Repornește Home Assistant.



\### HACS (Recomandat)

1\. Deschide HACS în Home Assistant.

2\. Click pe cele trei puncte din dreapta sus și selectează "Custom repositories".

3\. Adaugă URL-ul acestui depozit (GitHub) și selectează "Integration" ca categorie.

4\. Click pe "Add", apoi caută "RER Group" în lista HACS și descarcă-l.

5\. Repornește Home Assistant.



\---



\## Configurare



1\. Mergi la Configurare (Settings) > Dispozitive și Servicii (Devices \& Services).

2\. Click pe butonul "Add Integration" (Adaugă Integrare) din dreapta jos.

3\. Caută "RER Group" în listă.

4\. Selectează Furnizorul de Servicii corespunzător (ex: Retim Timișoara).

5\. Introdu adresa de E-mail și Parola folosite pe portalul oficial.

6\. Click pe Submit.



\---



\## Detalii Tehnice

\* Interval de Actualizare: Integrarea verifică datele la fiecare 3 ore pentru a evita blocarea contului, deoarece facturile nu se modifică frecvent.

\* Unități de Măsură: Valorile monetare sunt exprimate în RON.

\* Categorii: Senzorii cu date administrative sunt marcați ca "Diagnostic" pentru a nu aglomera interfața principală.



\## Depanare

Dacă întâmpini probleme la autentificare:

1\. Verifică datele de logare accesând manual portalul web al furnizorului.

2\. Verifică log-urile Home Assistant (Settings > System > Logs) pentru a vedea eroarea exactă.



\---



\## Declinarea Responsabilității

Această integrare este un proiect independent și NU este afiliată oficial sau aprobată de RER Group, RETIM, REBU sau alte filiale. Utilizarea se face pe propria răspundere.

