from flask import Flask, request, jsonify
from pulp import LpProblem, LpMaximize, LpVariable, lpSum, PULP_CBC_CMD, value

app = Flask(__name__)

@app.route("/optimize", methods=["POST"])
def optimize():
    try:
        data = request.get_json()
        orders = data["orders"]
        bom = data["bom"]
        stock = data["stock"]

        # Apelăm funcția de optimizare
        result = optimize_car_production(orders, bom, stock)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

def optimize_car_production(orders, bom, stock):
    problem = LpProblem("Maximizare_Comenzi", LpMaximize)
    products = list(orders.keys())
    product_vars = LpVariable.dicts("Produs", products, lowBound=0, cat="Integer")
    problem += lpSum([product_vars[p] for p in products]), "Total_Produse"

    for component, available in stock.items():
        total_used = lpSum(product_vars[p] for p in products if component in bom[p])
        problem += total_used <= available, f"Stoc_{component}"

    for p in products:
        problem += product_vars[p] <= orders[p], f"Comanda_{p}"

    problem.solve(PULP_CBC_CMD(msg=0))
    return {p: int(value(product_vars[p])) for p in products}

if __name__ == "__main__":
    app.run()
