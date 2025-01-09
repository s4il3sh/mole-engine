from flask import Flask, render_template, request
from sympy import symbols, Eq, solve
from sympy.chemistry import balance_stoichiometry
import pandas as pd
import os

app = Flask(__name__)

# Load atomic weights from ATOMS.LST
def load_atomic_weights(file_path):
    atomic_weights = {}
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            for line in f:
                parts = line.split()
                if len(parts) >= 2:
                    atomic_weights[parts[0]] = float(parts[1])
    return atomic_weights

atomic_weights = load_atomic_weights('ATOMS.LST')

# Function to calculate molar mass of a compound
def calculate_molar_mass(compound):
    from sympy.chemistry import parse_formula
    parsed_formula = parse_formula(compound)
    molar_mass = sum(atomic_weights[element] * count for element, count in parsed_formula.items())
    return molar_mass

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/calculate', methods=['POST'])
def calculate():
    try:
        reactants = request.form['reactants'].strip()
        products = request.form['products'].strip()

        reactants_dict, products_dict = balance_stoichiometry(
            reactants.split('+'), products.split('+')
        )

        # Calculate molar masses
        molar_masses = {compound: calculate_molar_mass(compound) for compound in {**reactants_dict, **products_dict}}

        # Collect data for display
        data = []
        for compound, coef in reactants_dict.items():
            data.append({
                'compound': compound,
                'molar_ratio': coef,
                'molar_mass': molar_masses[compound]
            })

        for compound, coef in products_dict.items():
            data.append({
                'compound': compound,
                'molar_ratio': coef,
                'molar_mass': molar_masses[compound]
            })

        return render_template('results.html', data=data)
    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == '__main__':
    app.run(debug=True)
