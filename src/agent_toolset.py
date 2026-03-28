from typing import Any
from pydantic import BaseModel
import re


# -----------------------------
# Request Models
# -----------------------------
class ConstructionRequest(BaseModel):
    query: str


# -----------------------------
# Toolset Class
# -----------------------------
class ConstructionAdvisorToolset:
    """AI-powered construction cost and decision advisor"""

    def __init__(self):
        pass

    # -----------------------------
    # 1. Parse Input
    # -----------------------------
    async def parse_input(self, query: str) -> dict:
        """Extract area and budget from user query"""
        try:
            area_match = re.search(r"(\d+)\s*(sq\s*ft|sqft)", query.lower())
            budget_match = re.search(r"(\d+)\s*(lakh|lac|₹|rs)?", query.lower())

            area = int(area_match.group(1)) if area_match else 1000
            budget = int(budget_match.group(1)) * 100000 if budget_match else 1000000

            return {
                "area": area,
                "budget": budget,
                "location": "India"
            }

        except Exception as e:
            return {"error": str(e)}

    # -----------------------------
    # 2. Cost Estimation
    # -----------------------------
    async def estimate_cost(self, area: int) -> dict:
        """Estimate construction cost based on area"""
        cost_per_sqft = 1500

        return {
            "foundation": area * 400,
            "structure": area * 600,
            "finishing": area * 500,
            "total": area * cost_per_sqft
        }

    # -----------------------------
    # 3. Material Suggestions
    # -----------------------------
    async def suggest_materials(self, budget: float) -> str:
        """Suggest cost-effective materials"""
        return (
            "• Use AAC blocks instead of traditional bricks\n"
            "• Use locally available materials\n"
            "• Avoid premium finishes initially\n"
        )

    # -----------------------------
    # 4. Risk Analysis
    # -----------------------------
    async def analyze_risk(self, budget: float, total_cost: float) -> str:
        """Analyze budget risk"""
        if budget < total_cost:
            return "⚠️ Budget is insufficient — may affect quality"
        return "✅ Budget is sufficient"

    # -----------------------------
    # 5. Optimization
    # -----------------------------
    async def optimize_budget(self) -> str:
        """Suggest cost optimization strategies"""
        return (
            "• Reduce finishing costs\n"
            "• Buy materials in bulk\n"
            "• Compare local suppliers\n"
        )

    # -----------------------------
    # 6. MAIN TOOL (IMPORTANT)
    # -----------------------------
    async def generate_construction_report(self, query: str) -> str:
        """Generate full construction analysis report"""

        parsed = await self.parse_input(query)
        if "error" in parsed:
            return f"Error parsing input: {parsed['error']}"

        cost = await self.estimate_cost(parsed["area"])
        materials = await self.suggest_materials(parsed["budget"])
        risk = await self.analyze_risk(parsed["budget"], cost["total"])
        optimization = await self.optimize_budget()

        return f"""
🏠 Smart Construction Report

📐 Area: {parsed['area']} sq ft  
💰 Budget: ₹{parsed['budget']:,}

📊 Cost Breakdown:
- Foundation: ₹{cost['foundation']:,}
- Structure: ₹{cost['structure']:,}
- Finishing: ₹{cost['finishing']:,}

💵 Estimated Total: ₹{cost['total']:,}

{risk}

🧱 Material Suggestions:
{materials}

💡 Optimization Tips:
{optimization}

🎯 Final Advice:
Ensure structural strength is not compromised. Adjust finishing based on budget.
"""

    # -----------------------------
    # REGISTER TOOLS
    # -----------------------------
    def get_tools(self) -> dict[str, Any]:
        return {
            "generate_construction_report": self,
        }