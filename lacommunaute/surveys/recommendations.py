from lacommunaute.surveys.models import Recommendation


def get_recommendations(dsp):
    recommendations = []
    recommendations.append(Recommendation.objects.get(codename=f"capacite-travail-{dsp.work_capacity}"))
    recommendations.append(Recommendation.objects.get(codename=f"cours-langue-{dsp.language_skills}"))
    recommendations.append(Recommendation.objects.get(codename=f"logement-{dsp.housing}"))
    recommendations.append(Recommendation.objects.get(codename=f"access-droits-{dsp.rights_access}"))
    recommendations.append(Recommendation.objects.get(codename=f"mobilite-{dsp.mobility}"))
    recommendations.append(Recommendation.objects.get(codename=f"ressources-{dsp.resources}"))
    recommendations.append(Recommendation.objects.get(codename=f"judiciaire-{dsp.judicial}"))
    recommendations.append(Recommendation.objects.get(codename=f"disponibilite-{dsp.availability}"))
    return recommendations
