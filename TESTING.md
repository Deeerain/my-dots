# Testing Guide for ubm-dots

## Quick Start

### 1. **Syntax & Import Checks** (быстро)
```bash
bash run_tests.sh
```

### 2. **Unit Tests** (требует pytest)
```bash
pip install pytest pytest-cov pytest-mock
pytest tests/ -v
```

### 3. **Coverage Report**
```bash
pytest tests/ --cov=. --cov-report=html
# Откройте htmlcov/index.html в браузере
```

### 4. **Docker Testing**
```bash
docker build -t ubm-dots-test .
docker run ubm-dots-test
```

---

## Test Structure

```
tests/
├── __init__.py
├── test_utils.py           # Unit tests for Utils class
├── test_update_service.py  # Unit tests for UpdateService
└── test_integration.py     # Integration tests for UBM
```

### test_utils.py
- Version comparison logic (`is_newest_version`)
- Version parsing and retrieval
- ZST installation

**Примеры тестов:**
```python
def test_major_version_newer(self):
    assert Utils.is_newest_version("2.0.0", "1.9.9") is True
```

### test_update_service.py
- GitHub API URL construction
- Repository info retrieval
- Asset finding and download info
- Update checking with mocks

**Примеры тестов:**
```python
def test_api_url_construction(self):
    service = UpdateService("ubm-dots", "deeerain")
    assert service.api_url == "https://api.github.com/repos/deeerain/ubm-dots"
```

### test_integration.py
- Setup functionality (symlink creation, backups)
- Restore functionality (symlink removal, backup restoration)
- Error handling

**Примеры тестов:**
```python
def test_setup_creates_symlinks(self, mock_config_dir, mock_dots_folder, temp_dirs):
    # Проверяет что setup правильно создает симлинки
```

---

## Running Tests

### Все тесты
```bash
pytest tests/
```

### Конкретный тест файл
```bash
pytest tests/test_utils.py -v
```

### Конкретный класс тестов
```bash
pytest tests/test_utils.py::TestIsNewestVersion -v
```

### Конкретный тест
```bash
pytest tests/test_utils.py::TestIsNewestVersion::test_major_version_newer -v
```

### С покрытием
```bash
pytest tests/ --cov=. --cov-report=term-missing
```

---

## CI/CD

Тесты автоматически запускаются при push в `main` или `dev`:

```
.github/workflows/tests.yml
├── Syntax check (все версии Python)
├── Import check
├── Unit tests (Python 3.12, 3.13, 3.14)
├── Coverage report (upload to Codecov)
└── Docker validation
```

---

## Зависимости для тестирования

### Обязательные (для базовых проверок)
- Python 3.12+
- typer
- urllib, json, subprocess, shutil, pathlib (встроенные)

### Опциональные (для полных тестов)
```bash
pip install pytest pytest-cov pytest-mock
```

### Для линтинга
```bash
pip install pylint black isort
```

### Для мультивер тестирования
```bash
pip install tox
tox  # Запустит тесты на всех версиях Python
```

---

## GitHub Actions Workflows

### tests.yml
- **test**: Unit tests на Python 3.12, 3.13, 3.14
- **syntax**: Проверка синтаксиса и импортов
- **docker**: Валидация PKGBUILD в Docker

---

## Линтинг и Форматирование

### Проверить код
```bash
pylint ubm_dots.py
black --check ubm_dots.py tests/
isort --check-only ubm_dots.py tests/
```

### Автоформатирование
```bash
black ubm_dots.py tests/
isort ubm_dots.py tests/
```

### С tox
```bash
tox -e lint      # Проверка
tox -e format    # Автоформат
tox -e coverage  # Покрытие
```

---

## Примеры использования

### Запустить быструю проверку перед коммитом
```bash
bash run_tests.sh
```

### Полная проверка перед PR
```bash
pip install pytest pytest-cov pytest-mock pylint
pytest tests/ -v --cov=.
pylint ubm_dots.py
```

### Развертывание с контролем качества
```bash
bash run_tests.sh && makepkg -isp PKGBUILD
```

---

## Troubleshooting

### "ModuleNotFoundError: No module named 'pytest'"
```bash
pip install pytest pytest-cov pytest-mock
```

### "CalledProcessError" в тестах
Это нормально - тесты мокируют syscalls. Проверьте что тесты проходят.

### Coverage низкий
Добавьте новые тесты для покрытия функциональности:
```bash
pytest tests/ --cov=. --cov-report=html
# Откройте htmlcov/index.html для деталей
```

---

## Добавление новых тестов

1. Создайте функцию с префиксом `test_`:
```python
def test_my_feature():
    assert my_function() == expected
```

2. Используйте fixtures для setup:
```python
@pytest.fixture
def temp_config(tmp_path):
    config = tmp_path / "config"
    config.mkdir()
    return config
```

3. Используйте mocks для внешних вызовов:
```python
@patch('subprocess.run')
def test_command(mock_run):
    mock_run.return_value = MagicMock(returncode=0)
```

4. Запустите:
```bash
pytest tests/test_new.py -v
```
