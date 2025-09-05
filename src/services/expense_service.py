"""
Serviço para gerenciamento de gastos.
"""
from datetime import datetime
from typing import List, Dict, Optional
from sqlalchemy import and_
from src.models.user import db
from src.models.expense import Expense, Category, UserSettings
from src.utils.helpers import get_period_dates


class ExpenseService:
    """Serviço para operações relacionadas a gastos."""

    @staticmethod
    def create_expense(user_phone: str, message_data: dict) -> Expense:
        """
        Cria um novo gasto.
        """
        expense = Expense.create_from_message_data(user_phone, message_data)
        db.session.add(expense)
        db.session.commit()
        return expense

    @staticmethod
    def get_expenses_by_user(user_phone: str, limit: int = 100) -> List[Expense]:
        """
        Retorna gastos de um usuário.
        """
        return (
            Expense.query
            .filter(Expense.user_phone == user_phone)
            .order_by(Expense.created_at.desc())
            .limit(limit)
            .all()
        )

    @staticmethod
    def get_expenses_by_period(user_phone: str, period: str, category: Optional[str] = None) -> List[Expense]:
        """
        Retorna gastos de um período específico.
        """
        start_date, end_date = get_period_dates(period)

        query = Expense.query.filter(
            and_(
                Expense.user_phone == user_phone,
                Expense.created_at >= start_date,
                Expense.created_at <= end_date,
            )
        )

        if category and category != "todas as categorias":
            query = query.filter(Expense.category == category)

        return query.order_by(Expense.created_at.desc()).all()

    @staticmethod
    def get_total_by_period(user_phone: str, period: str, category: Optional[str] = None) -> float:
        """
        Retorna o total gasto em um período (consulta agregada no banco).
        """
        start_date, end_date = get_period_dates(period)

        q = db.session.query(db.func.sum(Expense.amount)).filter(
            Expense.user_phone == user_phone,
            Expense.created_at >= start_date,
            Expense.created_at <= end_date,
        )

        if category and category != "todas as categorias":
            q = q.filter(Expense.category == category)

        total = q.scalar() or 0.0
        return float(total)

    @staticmethod
    def get_expenses_by_category(user_phone: str, category: str, limit: int = 50) -> List[Expense]:
        """
        Retorna gastos de uma categoria específica.
        """
        return (
            Expense.query
            .filter(Expense.user_phone == user_phone, Expense.category == category)
            .order_by(Expense.created_at.desc())
            .limit(limit)
            .all()
        )

    @staticmethod
    def get_category_summary(user_phone: str, period: str = "month") -> List[Dict]:
        """
        Retorna resumo por categoria (total e contagem) no período.
        """
        start_date, end_date = get_period_dates(period)

        results = (
            db.session.query(
                Expense.category,
                db.func.sum(Expense.amount).label("total"),
                db.func.count(1).label("count"),
            )
            .filter(
                Expense.user_phone == user_phone,
                Expense.created_at >= start_date,
                Expense.created_at <= end_date,
            )
            .group_by(Expense.category)
            .all()
        )

        return [
            {"category": r.category if hasattr(r, "category") else r[0], "total": float(r.total), "count": int(r.count)}
            for r in results
        ]

    @staticmethod
    def update_expense(expense_id: int, **kwargs) -> Optional[Expense]:
        """
        Atualiza um gasto.
        """
        expense = Expense.query.get(expense_id)
        if not expense:
            return None

        for key, value in kwargs.items():
            if hasattr(expense, key):
                setattr(expense, key, value)

        expense.updated_at = datetime.utcnow()
        db.session.commit()
        return expense

    @staticmethod
    def delete_expense(expense_id: int, user_phone: str) -> bool:
        """
        Deleta um gasto validando o telefone do usuário.
        """
        expense = Expense.query.filter(Expense.id == expense_id, Expense.user_phone == user_phone).first()
        if not expense:
            return False

        db.session.delete(expense)
        db.session.commit()
        return True

    @staticmethod
    def get_user_statistics(user_phone: str) -> Dict:
        """
        Retorna estatísticas do usuário.
        """
        # Total geral (contagem de registros)
        total_expenses = db.session.query(db.func.count(1)).filter(Expense.user_phone == user_phone).scalar() or 0
        total_expenses = int(total_expenses)

        # Soma total
        total_amount = db.session.query(db.func.sum(Expense.amount)).filter(Expense.user_phone == user_phone).scalar() or 0.0
        total_amount = float(total_amount)

        # Totais por período (usa a versão agregada, mais performática)
        today_total = ExpenseService.get_total_by_period(user_phone, "today")
        week_total = ExpenseService.get_total_by_period(user_phone, "week")
        month_total = ExpenseService.get_total_by_period(user_phone, "month")

        # Categoria mais usada
        row = (
            db.session.query(Expense.category, db.func.count(1).label("count"))
            .filter(Expense.user_phone == user_phone)
            .group_by(Expense.category)
            .order_by(db.func.count(1).desc())
            .first()
        )

        most_used_category_name = None
        if row:
            # row pode ser KeyedTuple com atributo 'category' ou tupla => extrai com segurança
            most_used_category_name = getattr(row, "category", None) or (row[0] if len(row) > 0 else None)

        return {
            "total_expenses": total_expenses,
            "total_amount": float(total_amount),
            "today_total": float(today_total),
            "week_total": float(week_total),
            "month_total": float(month_total),
            "most_used_category": most_used_category_name,
        }


class CategoryService:
    """Serviço para gerenciamento de categorias."""

    @staticmethod
    def get_all_categories() -> List[Category]:
        """Retorna todas as categorias ativas."""
        return Category.query.filter_by(is_active=True).all()

    @staticmethod
    def create_category(name: str, description: str = None, emoji: str = None) -> Category:
        """Cria uma nova categoria."""
        category = Category(name=name.lower(), description=description, emoji=emoji)
        db.session.add(category)
        db.session.commit()
        return category

    @staticmethod
    def initialize_default_categories():
        """Inicializa as categorias padrão se não existirem."""
        from src.config.settings import Config
        from src.utils.helpers import get_emoji_for_category

        existing_categories = {cat.name for cat in CategoryService.get_all_categories()}

        for category_name in Config.DEFAULT_CATEGORIES:
            if category_name not in existing_categories:
                CategoryService.create_category(
                    name=category_name,
                    description=f"Categoria {category_name}",
                    emoji=get_emoji_for_category(category_name),
                )


class UserSettingsService:
    """Serviço para configurações do usuário."""

    @staticmethod
    def get_or_create_settings(user_phone: str) -> UserSettings:
        """Retorna ou cria configurações do usuário."""
        settings = UserSettings.query.filter_by(user_phone=user_phone).first()
        if not settings:
            settings = UserSettings(user_phone=user_phone)
            db.session.add(settings)
            db.session.commit()
        return settings

    @staticmethod
    def update_settings(user_phone: str, **kwargs) -> UserSettings:
        """Atualiza configurações do usuário."""
        settings = UserSettingsService.get_or_create_settings(user_phone)
        for key, value in kwargs.items():
            if hasattr(settings, key):
                setattr(settings, key, value)
        settings.updated_at = datetime.utcnow()
        db.session.commit()
        return settings
