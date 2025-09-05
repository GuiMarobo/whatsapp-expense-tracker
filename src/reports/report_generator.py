"""
Gerador de relatórios e análises de gastos.
"""
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import io
import base64
from src.services.expense_service import ExpenseService
from src.utils.helpers import format_currency, get_period_dates, get_emoji_for_category

# Configurar matplotlib para usar fonte que suporte caracteres especiais
plt.rcParams['font.family'] = ['DejaVu Sans', 'Liberation Sans', 'sans-serif']
plt.rcParams['axes.unicode_minus'] = False

class ReportGenerator:
    """Gerador de relatórios e visualizações de gastos."""
    
    @staticmethod
    def generate_expense_summary(user_phone: str, period: str = 'month') -> Dict:
        """
        Gera resumo de gastos para um período.
        
        Args:
            user_phone (str): Telefone do usuário
            period (str): Período ('today', 'week', 'month', 'year', 'all')
            
        Returns:
            Dict: Resumo dos gastos
        """
        # Obtém dados do período
        expenses = ExpenseService.get_expenses_by_period(user_phone, period)
        category_summary = ExpenseService.get_category_summary(user_phone, period)
        
        # Calcula estatísticas
        total_amount = sum(expense.amount for expense in expenses)
        total_count = len(expenses)
        
        # Média por gasto
        avg_per_expense = total_amount / total_count if total_count > 0 else 0
        
        # Categoria com maior gasto
        top_category = None
        if category_summary:
            top_category = max(category_summary, key=lambda x: x['total'])
        
        # Período de datas
        start_date, end_date = get_period_dates(period)
        
        return {
            'period': period,
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
            'total_amount': total_amount,
            'total_count': total_count,
            'avg_per_expense': avg_per_expense,
            'top_category': top_category,
            'category_breakdown': category_summary,
            'expenses': [expense.to_dict() for expense in expenses]
        }
    
    @staticmethod
    def generate_category_chart(user_phone: str, period: str = 'month', 
                              save_path: Optional[str] = None) -> str:
        """
        Gera gráfico de pizza por categoria.
        
        Args:
            user_phone (str): Telefone do usuário
            period (str): Período
            save_path (str, optional): Caminho para salvar o gráfico
            
        Returns:
            str: Caminho do arquivo ou base64 da imagem
        """
        category_summary = ExpenseService.get_category_summary(user_phone, period)
        
        if not category_summary:
            return None
        
        # Prepara dados
        categories = [item['category'].title() for item in category_summary]
        amounts = [item['total'] for item in category_summary]
        
        # Cria o gráfico
        plt.figure(figsize=(10, 8))
        colors = plt.cm.Set3(range(len(categories)))
        
        wedges, texts, autotexts = plt.pie(
            amounts, 
            labels=categories,
            autopct='%1.1f%%',
            colors=colors,
            startangle=90
        )
        
        # Personaliza o gráfico
        plt.title(f'Gastos por Categoria - {period.title()}', fontsize=16, fontweight='bold')
        
        # Adiciona legenda com valores
        legend_labels = [f'{cat}: {format_currency(amt)}' 
                        for cat, amt in zip(categories, amounts)]
        plt.legend(wedges, legend_labels, title="Categorias", 
                  loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            plt.close()
            return save_path
        else:
            # Retorna como base64
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.getvalue()).decode()
            plt.close()
            return image_base64
    
    @staticmethod
    def generate_timeline_chart(user_phone: str, period: str = 'month',
                              save_path: Optional[str] = None) -> str:
        """
        Gera gráfico de linha temporal dos gastos.
        
        Args:
            user_phone (str): Telefone do usuário
            period (str): Período
            save_path (str, optional): Caminho para salvar o gráfico
            
        Returns:
            str: Caminho do arquivo ou base64 da imagem
        """
        expenses = ExpenseService.get_expenses_by_period(user_phone, period)
        
        if not expenses:
            return None
        
        # Converte para DataFrame
        df = pd.DataFrame([expense.to_dict() for expense in expenses])
        df['created_at'] = pd.to_datetime(df['created_at'])
        df['date'] = df['created_at'].dt.date
        
        # Agrupa por data
        daily_totals = df.groupby('date')['amount'].sum().reset_index()
        
        # Cria o gráfico
        plt.figure(figsize=(12, 6))
        plt.plot(daily_totals['date'], daily_totals['amount'], 
                marker='o', linewidth=2, markersize=6)
        
        # Personaliza o gráfico
        plt.title(f'Gastos Diários - {period.title()}', fontsize=16, fontweight='bold')
        plt.xlabel('Data', fontsize=12)
        plt.ylabel('Valor (R$)', fontsize=12)
        plt.grid(True, alpha=0.3)
        
        # Formata eixo X
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%d/%m'))
        plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=max(1, len(daily_totals) // 10)))
        plt.xticks(rotation=45)
        
        # Adiciona valores nos pontos
        for i, row in daily_totals.iterrows():
            plt.annotate(f'R$ {row["amount"]:.0f}', 
                        (row['date'], row['amount']),
                        textcoords="offset points", 
                        xytext=(0,10), 
                        ha='center', fontsize=9)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            plt.close()
            return save_path
        else:
            # Retorna como base64
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.getvalue()).decode()
            plt.close()
            return image_base64
    
    @staticmethod
    def generate_comparison_chart(user_phone: str, save_path: Optional[str] = None) -> str:
        """
        Gera gráfico comparativo entre períodos.
        
        Args:
            user_phone (str): Telefone do usuário
            save_path (str, optional): Caminho para salvar o gráfico
            
        Returns:
            str: Caminho do arquivo ou base64 da imagem
        """
        # Obtém dados de diferentes períodos
        periods = ['today', 'week', 'month']
        period_names = ['Hoje', 'Esta Semana', 'Este Mês']
        totals = []
        
        for period in periods:
            total = ExpenseService.get_total_by_period(user_phone, period)
            totals.append(total)
        
        # Cria o gráfico
        plt.figure(figsize=(10, 6))
        bars = plt.bar(period_names, totals, color=['#FF6B6B', '#4ECDC4', '#45B7D1'])
        
        # Personaliza o gráfico
        plt.title('Comparativo de Gastos por Período', fontsize=16, fontweight='bold')
        plt.ylabel('Valor (R$)', fontsize=12)
        plt.grid(True, alpha=0.3, axis='y')
        
        # Adiciona valores nas barras
        for bar, total in zip(bars, totals):
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height + max(totals) * 0.01,
                    format_currency(total), ha='center', va='bottom', fontsize=11)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            plt.close()
            return save_path
        else:
            # Retorna como base64
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.getvalue()).decode()
            plt.close()
            return image_base64
    
    @staticmethod
    def generate_detailed_report(user_phone: str, period: str = 'month') -> str:
        """
        Gera relatório detalhado em texto.
        
        Args:
            user_phone (str): Telefone do usuário
            period (str): Período
            
        Returns:
            str: Relatório formatado
        """
        summary = ReportGenerator.generate_expense_summary(user_phone, period)
        
        # Cabeçalho
        period_names = {
            'today': 'Hoje',
            'yesterday': 'Ontem',
            'week': 'Esta Semana',
            'month': 'Este Mês',
            'year': 'Este Ano',
            'all': 'Período Total'
        }
        
        period_name = period_names.get(period, period)
        
        report = f"📊 *RELATÓRIO DETALHADO - {period_name.upper()}*\n"
        report += "=" * 40 + "\n\n"
        
        # Resumo geral
        report += f"💰 *Total Gasto:* {format_currency(summary['total_amount'])}\n"
        report += f"📝 *Número de Gastos:* {summary['total_count']}\n"
        
        if summary['total_count'] > 0:
            report += f"📊 *Média por Gasto:* {format_currency(summary['avg_per_expense'])}\n"
        
        report += "\n"
        
        # Top categoria
        if summary['top_category']:
            top_cat = summary['top_category']
            emoji = get_emoji_for_category(top_cat['category'])
            report += f"{emoji} *Categoria com Maior Gasto:* {top_cat['category'].title()}\n"
            report += f"   Valor: {format_currency(top_cat['total'])} ({top_cat['count']} gastos)\n\n"
        
        # Breakdown por categoria
        if summary['category_breakdown']:
            report += "*GASTOS POR CATEGORIA:*\n"
            report += "-" * 25 + "\n"
            
            for item in summary['category_breakdown']:
                emoji = get_emoji_for_category(item['category'])
                percentage = (item['total'] / summary['total_amount']) * 100 if summary['total_amount'] > 0 else 0
                
                report += f"{emoji} *{item['category'].title()}*\n"
                report += f"   {format_currency(item['total'])} ({percentage:.1f}%) - {item['count']} gastos\n"
            
            report += "\n"
        
        # Últimos gastos
        if summary['expenses']:
            report += "*ÚLTIMOS GASTOS:*\n"
            report += "-" * 15 + "\n"
            
            recent_expenses = sorted(summary['expenses'], 
                                   key=lambda x: x['created_at'], reverse=True)[:5]
            
            for expense in recent_expenses:
                date = datetime.fromisoformat(expense['created_at']).strftime('%d/%m %H:%M')
                emoji = get_emoji_for_category(expense['category'])
                
                report += f"{emoji} {format_currency(expense['amount'])} - {expense['category'].title()}\n"
                report += f"   {expense['description']} ({date})\n"
        
        return report
    
    @staticmethod
    def export_to_csv(user_phone: str, period: str = 'month', 
                     file_path: str = None) -> str:
        """
        Exporta gastos para CSV.
        
        Args:
            user_phone (str): Telefone do usuário
            period (str): Período
            file_path (str, optional): Caminho do arquivo
            
        Returns:
            str: Caminho do arquivo CSV
        """
        expenses = ExpenseService.get_expenses_by_period(user_phone, period)
        
        if not expenses:
            return None
        
        # Converte para DataFrame
        df = pd.DataFrame([expense.to_dict() for expense in expenses])
        
        # Seleciona e renomeia colunas
        df = df[['created_at', 'amount', 'category', 'description', 'confidence']]
        df.columns = ['Data', 'Valor', 'Categoria', 'Descrição', 'Confiança']
        
        # Formata data
        df['Data'] = pd.to_datetime(df['Data']).dt.strftime('%d/%m/%Y %H:%M')
        
        # Define caminho do arquivo
        if not file_path:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            file_path = f'gastos_{user_phone}_{period}_{timestamp}.csv'
        
        # Salva CSV
        df.to_csv(file_path, index=False, encoding='utf-8-sig')
        
        return file_path

