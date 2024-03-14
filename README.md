Курсовая работа по базам данных варианта 15

Решением является создание телеграмм бота, который взаимодействует с базой данных, позволяет добавлять, редактировать, удалять каждое поле из 6 таблиц А также удобный пользовательский интерфейс

Реализован бот на библиотеке aiogramm 3.2 и sqlachemy

Структура бота:

run - файл отвечающий за запуск бота

models - описание базы данных, добавление асинхронного контекста для взамойдействия с данными

handlers - файл реагирующий на взаимодействия с ботом от действий пользователя

admin - файл реагирующий на взаимодейтсвие с ботом от действия администратора (в т.ч. и выход отчётов)

reuests и requests_a - файлы для запросов к базе данных

keyboards - файл для создания различных инлайн клавиатур с данными из бд

 БД «Авиакомпании»
Необходимо хранить информацию об авиакомпаниях (шифр, название, адрес), кассах (номер, 
адрес), кассирах (табельный номер, ФИО). Клиенты (номер и серия паспорта, ФИО) приобретают 
билеты (номер, тип, дата продажи, касса, кассир, авиакомпания). Билет содержит не более четырех 
купонов (номер, направление полета, тариф, клиент).
  Выходные документы:
1. Билеты, проданные за указанный месяц указанной авиакомпании.
2. Общая сумма от продаж билетов каждой авиакомпании.
3. Список клиентов авиакомпаний на заданную дату.