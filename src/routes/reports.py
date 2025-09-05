"""
Rotas para relatórios e análises.
"""
from flask import Blueprint, request, jsonify, send_file
from src.reports.report_generator import ReportGenerator
from src.services.expense_service import ExpenseService
import os
import tempfile

reports_bp = Blueprint('reports', __name__)

@reports_bp.route('/reports/summary/<user_phone>')
def get_expense_summary(user_phone):
    """Retorna resumo de gastos do usuário."""
    
    period = request.args.get('period', 'month')
    
    try:
        summary = ReportGenerator.generate_expense_summary(user_phone, period)
        return jsonify({
            'status': 'success',
            'data': summary
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@reports_bp.route('/reports/chart/category/<user_phone>')
def get_category_chart(user_phone):
    """Retorna gráfico de pizza por categoria."""
    
    period = request.args.get('period', 'month')
    
    try:
        # Gera gráfico temporário
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
            chart_path = ReportGenerator.generate_category_chart(
                user_phone, period, tmp_file.name
            )
            
            if chart_path:
                return send_file(chart_path, mimetype='image/png')
            else:
                return jsonify({
                    'status': 'error',
                    'message': 'Nenhum dado encontrado para o período'
                }), 404
                
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500
    finally:
        # Limpa arquivo temporário
        if 'chart_path' in locals() and chart_path and os.path.exists(chart_path):
            os.unlink(chart_path)

@reports_bp.route('/reports/chart/timeline/<user_phone>')
def get_timeline_chart(user_phone):
    """Retorna gráfico de linha temporal."""
    
    period = request.args.get('period', 'month')
    
    try:
        # Gera gráfico temporário
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
            chart_path = ReportGenerator.generate_timeline_chart(
                user_phone, period, tmp_file.name
            )
            
            if chart_path:
                return send_file(chart_path, mimetype='image/png')
            else:
                return jsonify({
                    'status': 'error',
                    'message': 'Nenhum dado encontrado para o período'
                }), 404
                
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500
    finally:
        # Limpa arquivo temporário
        if 'chart_path' in locals() and chart_path and os.path.exists(chart_path):
            os.unlink(chart_path)

@reports_bp.route('/reports/chart/comparison/<user_phone>')
def get_comparison_chart(user_phone):
    """Retorna gráfico comparativo entre períodos."""
    
    try:
        # Gera gráfico temporário
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
            chart_path = ReportGenerator.generate_comparison_chart(
                user_phone, tmp_file.name
            )
            
            if chart_path:
                return send_file(chart_path, mimetype='image/png')
            else:
                return jsonify({
                    'status': 'error',
                    'message': 'Nenhum dado encontrado'
                }), 404
                
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500
    finally:
        # Limpa arquivo temporário
        if 'chart_path' in locals() and chart_path and os.path.exists(chart_path):
            os.unlink(chart_path)

@reports_bp.route('/reports/detailed/<user_phone>')
def get_detailed_report(user_phone):
    """Retorna relatório detalhado em texto."""
    
    period = request.args.get('period', 'month')
    
    try:
        report = ReportGenerator.generate_detailed_report(user_phone, period)
        return jsonify({
            'status': 'success',
            'data': {
                'report': report,
                'period': period
            }
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@reports_bp.route('/reports/export/csv/<user_phone>')
def export_csv(user_phone):
    """Exporta gastos para CSV."""
    
    period = request.args.get('period', 'month')
    
    try:
        # Gera CSV temporário
        with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as tmp_file:
            csv_path = ReportGenerator.export_to_csv(
                user_phone, period, tmp_file.name
            )
            
            if csv_path:
                return send_file(
                    csv_path, 
                    mimetype='text/csv',
                    as_attachment=True,
                    download_name=f'gastos_{user_phone}_{period}.csv'
                )
            else:
                return jsonify({
                    'status': 'error',
                    'message': 'Nenhum dado encontrado para exportar'
                }), 404
                
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500
    finally:
        # Limpa arquivo temporário
        if 'csv_path' in locals() and csv_path and os.path.exists(csv_path):
            os.unlink(csv_path)

@reports_bp.route('/reports/statistics/<user_phone>')
def get_user_statistics(user_phone):
    """Retorna estatísticas do usuário."""
    
    try:
        stats = ExpenseService.get_user_statistics(user_phone)
        return jsonify({
            'status': 'success',
            'data': stats
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@reports_bp.route('/reports/categories/<user_phone>')
def get_category_summary(user_phone):
    """Retorna resumo por categorias."""
    
    period = request.args.get('period', 'month')
    
    try:
        summary = ExpenseService.get_category_summary(user_phone, period)
        return jsonify({
            'status': 'success',
            'data': summary
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

