import sqlite3
from pathlib import Path
from faker import Faker
import random
from tabulate import tabulate

fake = Faker(locals="fr_FR")

class Magasin:
    def __init__(self):
        self.connexion = self.connecter_base_de_donnees()
        self.curseur = self.connexion.cursor()
        # Créer la table articles lors de l'initialisation de la classe :
        self.creer_table_articles()


    def connecter_base_de_donnees(self):
        cur_dir = Path(__file__).parent
        fichier = "data_base.db"
        chemin = cur_dir / fichier
        connexion = sqlite3.connect(chemin)
        return connexion


    def creer_table_articles(self):
        self.curseur.execute(""" 
        CREATE TABLE IF NOT EXISTS articles(
                  Reference text,
                  Vetement text,
                  Couleur text,
                  Taille text,
                  Quantite integer,
                  Prix_unitaire float,
                  Prix_total decimal
        )
        """)
        self.connexion.commit()


    @staticmethod
    def reference_aleatoire():
        lettre_maj = fake.random_uppercase_letter()
        suite_de_nombre = fake.numerify('#####')
        return lettre_maj + suite_de_nombre


    @staticmethod
    def vetement_aleatoire():
        categories = [
            "chemise", "pantalon", "robe", "jupe", "veste",
            "pull", "t-shirt", "costume", "manteau", "blouson",
            "chaussures", "chaussettes", "cravate", "ceinture", "casquette"
        ]
        return random.choice(categories)


    @staticmethod
    def couleur_aleatoire():
        colors_fr = [
            "rouge", "vert", "bleu", "jaune", "orange",
            "violet", "rose", "noir", "blanc", "gris",
            "marron", "argent", "or", "cyan", "indigo"
        ]
        return random.choice(colors_fr)


    @staticmethod
    def taille_aleatoire():
        taille_fr = ["XS", "S", "M", "L", "XL"]
        return random.choice(taille_fr)


    @staticmethod
    def prix_unitaire_aleatoire():
        return round(random.uniform(1, 100), 2)


    @staticmethod
    def quantite_aleatoire():
        return random.randint(1, 99)


    @staticmethod
    def calculer_prix_total(quantite, prix_unitaire):
        prix_total = quantite * prix_unitaire
        return f"{prix_total:.2f} €"


    def generer_stock(self):
        data = []
        for _ in range(5):
            reference = self.reference_aleatoire()
            vetement = self.vetement_aleatoire()
            couleur = self.couleur_aleatoire()
            taille = self.taille_aleatoire()
            quantite = self.quantite_aleatoire()
            prix_unitaire = self.prix_unitaire_aleatoire()
            prix_total = self.calculer_prix_total(quantite, prix_unitaire)
            data.append([reference, vetement, couleur, taille, quantite, prix_unitaire, prix_total])
        return data


    def insertion_bdd(self, data):
        for row in data:
            self.curseur.execute(""" 
            INSERT INTO articles(reference, vetement, couleur, taille, quantite, prix_unitaire, prix_total)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """, row)
        self.connexion.commit()


    def afficher_bdd(self):
        self.curseur.execute("SELECT * FROM articles ORDER BY prix_unitaire")
        afficher_bdd = self.curseur.fetchall()
        headers = ["Référence", "Vêtement", "Couleur", "Taille", "Quantité", "Prix unitaire", "Prix total"]
        print("\n" + tabulate(afficher_bdd, headers=headers))


    def afficher_vetement_en_stock(self):
        self.curseur.execute("SELECT Vetement FROM articles")
        afficher_vetement_disponible = self.curseur.fetchall()
        headers = ["Référence", "Vêtement", "Couleur", "Taille", "Quantité", "Prix unitaire", "Prix total"]
        print("\n" + tabulate(afficher_vetement_disponible, headers=headers))
    

    def afficher_vetement_saisie(self):
        saisie1 = input("Entrez un vêtement :\n👉 ")
        self.curseur.execute(f"SELECT * FROM articles WHERE Vetement = ?", (saisie1,))
        afficher_vetement_saisie = self.curseur.fetchall()
    
        if not afficher_vetement_saisie:
            print(f"Il n'y a pas de {saisie1} en stock.")
        else:
            headers = ["Référence", "Vêtement", "Couleur", "Taille", "Quantité", "Prix unitaire", "Prix total"]
            print("\n" + tabulate(afficher_vetement_saisie, headers=headers))


    def afficher_taille(self):
        while True:
            saisie2a = input("entrez une taille de vetement : \n👉 ")
            if saisie2a in ["XS", "S", "M", "L", "XL"]:
                break
            else:
                print("\n Veuillez entrer une taille valide : 'XS', 'S', 'M', 'L', 'XL'")

        while True:
            validation = input("Voulez-vous entrer une autre taille? oui / non \n👉 ")
            if validation in ["oui", "non"]:
                break
            else:
                print("\n Veuillez entrer oui ou non")

        if validation == "oui":
            saisie2b = input("entrez une autre taille de vetement : \n👉 ")
            while saisie2b not in ["XS", "S", "M", "L", "XL"]:
                print("Veuillez entrer une taille valide : 'XS', 'S', 'M', 'L', 'XL'")
                saisie2b = input("entrez une autre taille de vetement : \n👉 ")

        # Afficher les tailles disponibles :
        condition_taille = f"WHERE Taille = '{saisie2a}'"
        if validation == "oui":
            condition_taille += f" OR Taille = '{saisie2b}'"
        self.curseur.execute(f"SELECT* FROM articles {condition_taille} ORDER BY Taille")
        afficher_taille_saisie = self.curseur.fetchall()

        # Vérifier si la saisie figure bien dans la bdd :
        if not afficher_taille_saisie:
            print(f"Il n'y a pas de vêtement à votre taille en stock.")
        else:
            # Affichage des données dans le terminal
            headers = ["Référence", "Vêtement", "Couleur", "Taille", "Quantité", "Prix unitaire", "Prix total"]
            print("\n" + tabulate(afficher_taille_saisie, headers=headers))


    def afficher_articles_par_prix(self, comparaison):
        if comparaison == "<":
            texte_comparaison = "inférieur"
        elif comparaison == ">":
            texte_comparaison = "supérieur"

        while True:
            saisie = input(f"Entrez la somme dont le prix de l'article doit être {texte_comparaison} à : \n👉 ")
            try:
                saisie_float = float(saisie)
                break
            except ValueError:
                print("\n Veuillez entrer un nombre valide.")
    
        # Afficher les articles en fonction du prix
        self.curseur.execute(f"SELECT * FROM articles WHERE Prix_unitaire {comparaison} {saisie} ORDER BY Prix_unitaire")
        articles = self.curseur.fetchall()
        # Vérifier si la saisie figure bien dans la base de données
        if not articles:
            print(f"Il n'y a pas d'articles dont le prix est {texte_comparaison} à {saisie} €.")
        else:
            # Affichage des données dans le terminal
            headers = ["Référence", "Vêtement", "Couleur", "Taille", "Quantité", "Prix unitaire", "Prix total"]
            print("\n" + tabulate(articles, headers=headers))


magasin = Magasin()

##########################################################################################################################

print("\nBienvenue au magasin !")       
while True:
    confirmation = input("Le magasin est vide pour le moment, appuyez sur Entrée pour générer un stock \n👉 ")
    if confirmation == "":
        break

data = magasin.generer_stock()
magasin.insertion_bdd(data)

print("\nVoici votre stock :")
magasin.afficher_bdd()

while True:
    validation = input("\nVoulez-vous ajouter plus de stock? oui / non \n👉 ")
    if validation in ["oui", "non"]:
        break

if validation == "oui":
    data = magasin.generer_stock()
    magasin.insertion_bdd(data)
    print("\nVoici votre nouveau stock :")
    magasin.afficher_bdd()

while True:
    print("\nVeuillez choisir une action :")
    validation = input(""" 
1 : Réafficher le stock
2 : Afficher tous les vêtements disponibles
3 : Afficher un vêtement en particulier
4 : Afficher une ou plusieurs tailles
5 : Afficher tout le stock au prix inférieur à votre budget  
6 : Afficher tout le stock au prix supérieur à votre budget 
7 : Quitter le programme            
👉 """)

    while validation not in ["1","2","3","4","5","6","7"]:
        validation = input("Veuillez choisir une action entre 1 et 7\n")

    if validation == "1":
        magasin.afficher_bdd()
    
    elif validation == "2":
        magasin.afficher_vetement_en_stock()
    
    elif validation == "3":
        magasin.afficher_vetement_saisie()
    
    elif validation == "4":
        magasin.afficher_taille()
    
    elif validation == "5":
        magasin.afficher_articles_par_prix("<")

    elif validation == "6":
        magasin.afficher_articles_par_prix(">")
    
    elif validation =="7":
        magasin.connexion.close()
        break