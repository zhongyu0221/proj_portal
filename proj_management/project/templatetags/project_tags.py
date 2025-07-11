from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.simple_tag
def get_project_category_badge(project_category, display_text=None):
    """
    根据项目类别返回带颜色的徽章HTML
    
    用法: {% get_project_category_badge project.project_category project.get_project_category_display %}
    """
    if display_text is None:
        display_text = project_category
    
    category_colors = {
        'EXPLORING': {
            'badge_class': 'badge-phoenix-primary',
            'icon': 'fas fa-search',
            'description': 'Research and exploration phase'
        },
        'RESEARCH': {
            'badge_class': 'badge-phoenix-info',
            'icon': 'fas fa-microscope',
            'description': 'In-depth research and analysis'
        },
        'DEVELOPMENT': {
            'badge_class': 'badge-phoenix-success',
            'icon': 'fas fa-code',
            'description': 'Active development work'
        },
        'TESTING': {
            'badge_class': 'badge-phoenix-warning',
            'icon': 'fas fa-vial',
            'description': 'Quality assurance and testing'
        },
        'DEPLOYMENT': {
            'badge_class': 'badge-phoenix-danger',
            'icon': 'fas fa-rocket',
            'description': 'Production deployment'
        },
        'MAINTENANCE': {
            'badge_class': 'badge-phoenix-secondary',
            'icon': 'fas fa-tools',
            'description': 'Ongoing maintenance and updates'
        }
    }
    
    # 获取类别配置，如果没有找到则使用默认值
    category_config = category_colors.get(project_category, {
        'badge_class': 'badge-phoenix-dark',
        'icon': 'fas fa-folder',
        'description': 'Other project type'
    })
    
    html = f'<span class="badge badge-phoenix {category_config["badge_class"]} fs-10">'
    html += f'<i class="{category_config["icon"]} me-1"></i>{display_text}'
    html += '</span>'
    
    return mark_safe(html)

@register.simple_tag
def get_project_category_info(project_category):
    """
    获取项目类别的详细信息
    
    用法: {% get_project_category_info project.project_category %}
    """
    category_info = {
        'EXPLORING': {
            'name': 'Exploring',
            'badge_class': 'badge-phoenix-primary',
            'icon': 'fas fa-search',
            'description': 'Research and exploration phase'
        },
        'RESEARCH': {
            'name': 'Research',
            'badge_class': 'badge-phoenix-info',
            'icon': 'fas fa-microscope',
            'description': 'In-depth research and analysis'
        },
        'DEVELOPMENT': {
            'name': 'Development',
            'badge_class': 'badge-phoenix-success',
            'icon': 'fas fa-code',
            'description': 'Active development work'
        },
        'TESTING': {
            'name': 'Testing',
            'badge_class': 'badge-phoenix-warning',
            'icon': 'fas fa-vial',
            'description': 'Quality assurance and testing'
        },
        'DEPLOYMENT': {
            'name': 'Deployment',
            'badge_class': 'badge-phoenix-danger',
            'icon': 'fas fa-rocket',
            'description': 'Production deployment'
        },
        'MAINTENANCE': {
            'name': 'Maintenance',
            'badge_class': 'badge-phoenix-secondary',
            'icon': 'fas fa-tools',
            'description': 'Ongoing maintenance and updates'
        }
    }
    
    return category_info.get(project_category, {
        'name': 'Other',
        'badge_class': 'badge-phoenix-dark',
        'icon': 'fas fa-folder',
        'description': 'Other project type'
    })

@register.simple_tag
def get_all_project_categories():
    """
    获取所有项目类别的信息，用于图例显示
    
    用法: {% get_all_project_categories as categories %}
    """
    return [
        {
            'code': 'EXPLORING',
            'name': 'Exploring',
            'badge_class': 'badge-phoenix-primary',
            'icon': 'fas fa-search',
            'description': 'Research and exploration phase'
        },
        {
            'code': 'RESEARCH',
            'name': 'Research',
            'badge_class': 'badge-phoenix-info',
            'icon': 'fas fa-microscope',
            'description': 'In-depth research and analysis'
        },
        {
            'code': 'DEVELOPMENT',
            'name': 'Development',
            'badge_class': 'badge-phoenix-success',
            'icon': 'fas fa-code',
            'description': 'Active development work'
        },
        {
            'code': 'TESTING',
            'name': 'Testing',
            'badge_class': 'badge-phoenix-warning',
            'icon': 'fas fa-vial',
            'description': 'Quality assurance and testing'
        },
        {
            'code': 'DEPLOYMENT',
            'name': 'Deployment',
            'badge_class': 'badge-phoenix-danger',
            'icon': 'fas fa-rocket',
            'description': 'Production deployment'
        },
        {
            'code': 'MAINTENANCE',
            'name': 'Maintenance',
            'badge_class': 'badge-phoenix-secondary',
            'icon': 'fas fa-tools',
            'description': 'Ongoing maintenance and updates'
        }
    ] 