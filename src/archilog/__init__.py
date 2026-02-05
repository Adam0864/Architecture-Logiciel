import click
import uuid
import sqlite3

from dataclasses import dataclass

db = sqlite3.connect("appli_cagnotte.db")
db.execute("CREATE TABLE if not exists cagnottes(nom, montant)")
db.execute("CREATE TABLE if not exists depenses(nomC,nomP,montant,date)")

@dataclass
class Item:
    id: uuid.UUID
    name: str


@click.group()
def cli():
    pass


@cli.command()
@click.option("-n", "--name", prompt="Name", help="The name of the item.")
def créerCagnotte(name: str):
    db.execute("INSERT into cagnottes(nom,montant) values (?,0)",(name,))
    db.commit()

@cli.command()
@click.option("-n", "--name", prompt="Name", help="The name of the item.")
def supprimerCagnotte(name: str):
    db.execute("delete from cagnottes where nom=?",(name,))
    db.execute("delete from depenses where nomC=?",(name))
    db.commit()

@cli.command()
def Afficher():
    print(db.execute("select * from cagnottes").fetchall())
    print(db.execute("select * from depenses").fetchall())

@cli.command()
@click.option( "--nomc", prompt="nomc", help="The name of the cagnotte.")
@click.option( "--nomp", prompt="nomp", help="The name of the participant.")
@click.option( "--montant", prompt="Montant", help="The montant of the depense.")
def créerDepense(nomc: str,nomp : str,montant:int):
    if (len(db.execute("SELECT * from depenses where nomP=? and nomC=?",(nomp,nomc)).fetchall())==1):
        db.execute("UPDATE from cagnottes set montant = montant + ? where nom=?",(montant,nomc))
        db.execute("UPDATE into depenses set montant = montant + ? and date = current_date where nomC = ? and nomP = ?",(montant,nomc,nomp))
        db.commit()
    else:
        db.execute("INSERT into depenses values (?,?,?,current_date)",(nomc,nomp,montant))
        db.commit()
        db.execute("UPDATE cagnottes set montant = montant + ? where nom = ?",(montant,nomc))
        db.commit()

@cli.command()
def supprimerTout():
    db.execute("delete from cagnottes")
    db.commit()
    db.execute("select * from depenses")
    db.commit()

@cli.command()
@click.option( "--nomc", prompt="nomc", help="The name of the cagnotte.")
@click.option( "--nomp", prompt="nomp", help="The name of the participant.")
def supprimerDepense(nomc: str,nomp: str):
    montant = db.execute("Select montant from depenses where nomc=? and nomp=?", (nomc,nomp)).fetchone()
    print(montant[0])
    db.execute("delete from depenses where nomC=? and nomP=?", (nomc,nomp))
    db.commit()
    db.execute("UPDATE cagnottes set montant = montant - ? where nom = ?", (montant[0], nomc))
    db.commit()

@cli.command()
@click.option( "--nomc", prompt="nomc", help="The name of the cagnotte.")
def calculeDesParts(nomc: str):
    montantTotal=db.execute("select montant from cagnottes where nom=?",(nomc,)).fetchone()
    nbPersonnes=len(db.execute("select * from depenses where nomC=?",(nomc,)).fetchall())
    TTCparpersonne = montantTotal[0] / nbPersonnes
    gagnant = {}
    perdant = {}
    personneList = db.execute("SELECT * from depenses where nomC=?",(nomc,)).fetchall()
    for personne in personneList:
        credit = float(personne[2])-TTCparpersonne
        if credit > 0:
            gagnant[personne[1]]=credit
        elif credit < 0:
            perdant[personne[1]]=credit

    for personneEndettée in perdant.keys():
        for riche in gagnant.keys():
            if perdant[personneEndettée]<0 and gagnant[riche]!=0:
                calcul = perdant[personneEndettée]+gagnant[riche]
                if calcul>0:
                    print(personneEndettée+" doit "+str(abs(perdant[personneEndettée]))+" à "+riche)
                    gagnant[riche] = calcul
                    perdant[personneEndettée] = 0
                else:
                    print(personneEndettée+" doit "+str(gagnant[riche])+" à "+riche)
                    gagnant[riche] = 0
                    perdant[personneEndettée] = calcul