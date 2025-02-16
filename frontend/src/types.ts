export interface Message {
  id: string;
  text: string;
  sender: 'user' | 'assistant';
  timestamp: Date;
}

export interface Action {
  id: string;
  name: string;
  description: string;
  icon: string;
}

export const AVAILABLE_ACTIONS: Action[] = [
  {
    id: 'create_ticket',
    name: 'Создать заявку',
    description: 'Создание заявки в поддержку',
    icon: 'ticket'
  },
  {
    id: 'call_elevator',
    name: 'Вызвать лифт',
    description: 'Вызов лифта на ваш этаж',
    icon: 'elevator'
  },
  {
    id: 'check_camera',
    name: 'Просмотр камеры',
    description: 'Просмотр камеры в подъезде',
    icon: 'camera'
  },
  {
    id: 'check_snow',
    name: 'Проверить сугробы',
    description: 'Проверка уровня снега',
    icon: 'snowflake'
  },
  {
    id: 'submit_meter_readings',
    name: 'Ввести показания',
    description: 'Ввод показаний счетчиков',
    icon: 'gauge'
  },
  {
    id: 'pay_utilities',
    name: 'Оплатить счета',
    description: 'Оплата коммунальных услуг',
    icon: 'credit-card'
  }
];