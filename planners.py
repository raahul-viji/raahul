from flask import Blueprint, request, jsonify
from services.recommender import generate_recommendation

planner_bp = Blueprint("planner_bp", __name__)


@planner_bp.route("/api/recommend", methods=["POST"])
def recommend():

    try:
        data = request.get_json() or {}

        planner_type = data.get("planner_type", "home")

        result = generate_recommendation(
            planner_type,
            data
        )

        return jsonify({
            "success": True,
            "planner_type": planner_type,
            "recommendation": result
        })

    except Exception as e:

        return jsonify({
            "success": False,
            "error": str(e)
        }), 500