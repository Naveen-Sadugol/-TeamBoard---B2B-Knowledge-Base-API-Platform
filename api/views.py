from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import Count, Q
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .models import KBEntry, QueryLog
from .permissions import IsAdminUser
from .serializers import (
    KBEntrySerializer,
    LoginSerializer,
    QuerySerializer,
    RegisterSerializer,
)


def build_access_token(user):
    return str(RefreshToken.for_user(user).access_token)


class RegisterView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        user = User.objects.create_user(
            username=data["username"],
            password=data["password"],
            email=data["email"],
        )

        company = user.company
        company.company_name = data["company_name"]
        company.save(update_fields=["company_name"])

        return Response(
            {
                "username": user.username,
                "company_name": company.company_name,
                "api_key": company.api_key,
                "access": build_access_token(user),
            },
            status=status.HTTP_201_CREATED,
        )


class LoginView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = authenticate(
            request,
            username=serializer.validated_data["username"],
            password=serializer.validated_data["password"],
        )
        if user is None:
            return Response(
                {"detail": "Invalid username or password."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        company = user.company
        return Response(
            {
                "access": build_access_token(user),
                "company_name": company.company_name,
                "api_key": company.api_key,
            },
            status=status.HTTP_200_OK,
        )


class QueryKnowledgeBaseView(APIView):
    def post(self, request):
        serializer = QuerySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        search_term = serializer.validated_data["search"]
        company = request.user.company

        with transaction.atomic():
            queryset = KBEntry.objects.filter(
                Q(question__icontains=search_term) | Q(answer__icontains=search_term)
            ).order_by("id")
            results = list(queryset)
            results_count = len(results)
            QueryLog.objects.create(
                company=company,
                search_term=search_term,
                results_count=results_count,
            )

        return Response(
            {
                "search": search_term,
                "count": results_count,
                "results": KBEntrySerializer(results, many=True).data,
            },
            status=status.HTTP_200_OK,
        )


class AdminUsageSummaryView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        total_queries = QueryLog.objects.aggregate(total=Count("id"))["total"] or 0
        active_companies = QueryLog.objects.values("company").distinct().count()
        top_search_terms = list(
            QueryLog.objects.values("search_term")
            .annotate(count=Count("id"))
            .order_by("-count", "search_term")[:5]
        )

        return Response(
            {
                "total_queries": total_queries,
                "active_companies": active_companies,
                "top_search_terms": top_search_terms,
            },
            status=status.HTTP_200_OK,
        )
