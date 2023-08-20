import os
import sys
import random
import argparse
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()

from datacenter.models import Mark, Schoolkid, Chastisement, Commendation, Lesson
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned


def fix_marks(pupil):
    Mark.objects.filter(schoolkid=pupil, points__in=[2, 3]).update(points=5)


def delete_chastisement(pupil):
    Chastisement.objects.filter(schoolkid=pupil).delete()


def get_random_lesson(pupil, subject):
    lessons = Lesson.objects.filter(year_of_study=pupil.year_of_study, group_letter=pupil.group_letter)
    if not subject:
        random_lesson = lessons.order_by('?').first()
        return random_lesson
    else:
        filtered_lessons = lessons.filter(subject__title__contains=subject)
        try:
            random_lesson = random.choice(filtered_lessons)
            return random_lesson
        except IndexError:
            print("Предмет с таким названием не найден. Проверьте правильно ли вы указали название")
            sys.exit(3)


def get_random_commendation():
    commendations = [
        "Молодец!",
        "Отлично!",
        "Хорошо!",
        "Гораздо лучше, чем я ожидал!",
        "Ты меня приятно удивил!",
        "Великолепно!",
        "Прекрасно!",
        "Ты меня очень обрадовал!",
        "Именно этого я давно ждал от тебя!",
        "Сказано здорово – просто и ясно!",
        "Ты, как всегда, точен!",
        "Очень хороший ответ!",
        "Талантливо!",
        "Ты сегодня прыгнул выше головы!",
        "Я поражен!"
    ]
    random_commendation = random.choice(commendations)
    return random_commendation


def validate_arguments(args):
    name_parts = args.name.split()
    if not args.name or len(name_parts) < 2:
        print("Ошибка: имя ученика должно состоять как минимум из имени и фамилии. Пожалуйста, проверьте ввод.")
        sys.exit(4)

    name_parts = args.name.split()
    if any(len(part) < 2 or len(part) > 40 for part in name_parts):
        print("Ошибка: имя и фамилия должны быть длиной от 2 до 40 символов.")
        sys.exit(5)

    if not all(part.isalpha() or part == '-' for part in args.name.replace(" ", "")):
        print("Ошибка: имя и фамилия должны состоять только из букв и дефисов.")
        sys.exit(6)

    if args.subject and (len(args.subject) < 2 or len(args.subject) > 30):
        print("Ошибка: название предмета должно быть длиной от 2 до 30 символов.")
        sys.exit(7)

    if not all(part[0].isupper() for part in name_parts):
        print("Ошибка: имя и фамилия должны начинаться с заглавной буквы.")
        sys.exit(8)


def get_pupil(args):
    try:
        pupil = Schoolkid.objects.get(full_name__contains=args.name)
        return pupil
    except Schoolkid.MultipleObjectsReturned:
        print("Найдено несколько учеников с таким именем. Уточните имя.")
        sys.exit(1)
    except Schoolkid.ObjectDoesNotExist:
        print("Ученик с таким именем не найден. Проверьте правильно ли вы указали имя")
        sys.exit(2)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Исправь оценки, удали замечания и добавь похвалу")
    parser.add_argument("--name", type=str, help="Имя ученика", default="Фролов Иван")
    parser.add_argument("--subject", type=str, help="По какому предмету добавить похвалу", default=None)

    args = parser.parse_args()
    validate_arguments(args)

    pupil = get_pupil(args)
    lesson = get_random_lesson(pupil, args.subject)
    fix_marks(pupil)
    delete_chastisement(pupil)
    commendation_text = get_random_commendation()
    Commendation.objects.create(
        text=commendation_text,
        created=lesson.date,
        schoolkid=pupil,
        subject=lesson.subject,
        teacher=lesson.teacher
    )