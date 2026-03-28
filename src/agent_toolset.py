import json
import re
from typing import Any


class TrustMeshAuditorToolset:
    """Toolset for auditing other agent responses under a zero-trust model."""

    def _find_issues(
        self,
        original_user_query: str,
        agent_response: str,
        metadata: str,
    ) -> list[str]:
        issues: list[str] = []

        query_tokens = {
            token
            for token in re.findall(r"[a-zA-Z]{4,}", original_user_query.lower())
            if token not in {'that', 'this', 'with', 'from', 'have', 'your', 'what'}
        }
        response_tokens = set(re.findall(r"[a-zA-Z]{4,}", agent_response.lower()))
        overlap = len(query_tokens.intersection(response_tokens))

        if query_tokens and overlap == 0:
            issues.append('missing context')

        evidence_markers = ['source', 'citation', 'according to', 'evidence', 'reference']
        has_numbers = bool(re.search(r"\b\d+(\.\d+)?\b", agent_response))
        has_evidence = any(marker in agent_response.lower() for marker in evidence_markers)
        if has_numbers and not has_evidence:
            issues.append('hallucination')

        if 'cannot both' in agent_response.lower() or 'therefore not' in agent_response.lower():
            issues.append('logical inconsistency')

        risk_markers = ['exploit', 'bypass', 'disable security', 'illegal', 'financial guarantee']
        if any(marker in agent_response.lower() for marker in risk_markers):
            issues.append('risk_flag')

        if metadata and 'high_risk' in metadata.lower() and 'risk_flag' not in issues:
            issues.append('risk_flag')

        return issues

    def _score_confidence(self, issues: list[str], metadata: str, agent_response: str) -> int:
        score = 90
        penalties = {
            'missing context': 20,
            'hallucination': 25,
            'logical inconsistency': 30,
            'risk_flag': 35,
        }
        for issue in issues:
            score -= penalties.get(issue, 10)

        if metadata and 'historical_reliability=' in metadata.lower():
            match = re.search(r"historical_reliability\s*=\s*(\d+)", metadata.lower())
            if match:
                reliability = max(0, min(100, int(match.group(1))))
                score = int(round((score * 0.7) + (reliability * 0.3)))

        if len(agent_response.strip()) < 40:
            score -= 10

        return max(0, min(100, score))

    async def evaluate_agent_output(
        self,
        original_user_query: str,
        agent_response: str,
        metadata: str = '',
    ) -> dict[str, Any]:
        """Audit another agent response and return strict TrustMesh JSON output."""
        issues = self._find_issues(original_user_query, agent_response, metadata)
        confidence_score = self._score_confidence(issues, metadata, agent_response)

        if 'risk_flag' in issues and confidence_score < 60:
            status = 'rejected'
        elif issues:
            status = 'needs_revision'
        else:
            status = 'validated'

        if status == 'validated':
            improved_response = agent_response.strip()
        else:
            improved_response = (
                'Original response requires revision before execution. '
                'Provide evidence-backed claims, remove unsafe content, and align strictly '
                'to the user query and constraints.'
            )

        explanation_steps = [
            '1. Compared response content against the original query for semantic alignment.',
            '2. Checked claims for evidence markers and unsupported numeric assertions.',
            '3. Screened for logical contradictions and high-risk signals.',
            '4. Computed confidence score from detected issues and optional reliability metadata.',
            f'5. Assigned final status={status} using zero-trust thresholds.',
        ]

        recommendations = [
            'Add verifiable sources or explicit evidence for all non-trivial claims.',
            'State assumptions explicitly and mark unknowns instead of guessing.',
            'Re-run audit after revising for safety, compliance, and user-intent alignment.',
        ]

        return {
            'status': status,
            'confidence_score': confidence_score,
            'issues_detected': issues,
            'improved_response': improved_response,
            'explanation': ' '.join(explanation_steps),
            'recommendations': recommendations,
        }

    async def normalize_audit_output(self, raw_output: str) -> dict[str, Any]:
        """Normalize model output into the strict TrustMesh schema when possible."""
        try:
            parsed = json.loads(raw_output)
            if isinstance(parsed, dict):
                return parsed
        except json.JSONDecodeError:
            pass

        return {
            'status': 'needs_revision',
            'confidence_score': 35,
            'issues_detected': ['missing context'],
            'improved_response': raw_output.strip(),
            'explanation': (
                'Model output was not strict JSON. Normalization fallback applied and '
                'manual review is required.'
            ),
            'recommendations': [
                'Return valid JSON object with all required TrustMesh fields.',
                'Avoid free-form prose outside the JSON envelope.',
            ],
        }

    def get_tools(self) -> dict[str, Any]:
        return {
            'evaluate_agent_output': self,
            'normalize_audit_output': self,
        }