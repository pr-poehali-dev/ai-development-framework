import { useState } from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import Icon from '@/components/ui/icon';

const Index = () => {
  const [activeSection, setActiveSection] = useState('chat');
  const [botStatus, setBotStatus] = useState<'active' | 'inactive'>('active');

  const stats = [
    { label: 'Пользователей', value: '1,234', icon: 'Users', gradient: 'gradient-primary' },
    { label: 'Сообщений', value: '45.6K', icon: 'MessageSquare', gradient: 'gradient-secondary' },
    { label: 'Изображений', value: '8,921', icon: 'Image', gradient: 'gradient-primary' },
    { label: 'Точность', value: '98.5%', icon: 'Target', gradient: 'gradient-secondary' },
  ];

  const sections = [
    { id: 'chat', label: 'Чат', icon: 'MessageCircle' },
    { id: 'generation', label: 'Генерация', icon: 'Sparkles' },
    { id: 'editor', label: 'Редактор', icon: 'Wand2' },
    { id: 'history', label: 'История', icon: 'History' },
    { id: 'profile', label: 'Профиль', icon: 'User' },
    { id: 'settings', label: 'Настройки', icon: 'Settings' },
  ];

  const recentChats = [
    { user: 'Алексей К.', message: 'Нарисуй космический корабль', time: '2 мин назад', avatar: '👨‍🚀' },
    { user: 'Мария С.', message: 'Редактируй фон на фото', time: '5 мин назад', avatar: '👩‍🎨' },
    { user: 'Дмитрий В.', message: 'Расскажи про квантовую физику', time: '12 мин назад', avatar: '🧑‍🔬' },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-blue-50 to-pink-50">
      <div className="fixed top-0 left-0 w-full backdrop-blur-md bg-white/80 border-b border-purple-100 z-50">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 rounded-2xl gradient-primary flex items-center justify-center shadow-lg">
                <Icon name="Bot" size={28} className="text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold gradient-text">AI Assistant Bot</h1>
                <p className="text-sm text-muted-foreground">Умный помощник нового поколения</p>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <Badge 
                variant={botStatus === 'active' ? 'default' : 'secondary'}
                className={`${botStatus === 'active' ? 'gradient-primary' : ''} text-white px-4 py-2 text-sm`}
              >
                <span className={`w-2 h-2 rounded-full bg-white mr-2 ${botStatus === 'active' ? 'animate-pulse-soft' : ''}`}></span>
                {botStatus === 'active' ? 'Активен' : 'Неактивен'}
              </Badge>
              <Button 
                onClick={() => setBotStatus(botStatus === 'active' ? 'inactive' : 'active')}
                className="gradient-secondary shadow-lg hover:shadow-xl transition-all"
              >
                <Icon name="Power" size={18} className="mr-2" />
                {botStatus === 'active' ? 'Остановить' : 'Запустить'}
              </Button>
            </div>
          </div>
        </div>
      </div>

      <div className="container mx-auto px-6 pt-32 pb-12">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          {stats.map((stat, index) => (
            <Card 
              key={index} 
              className="p-6 border-0 shadow-lg hover:shadow-xl transition-all duration-300 hover:-translate-y-1 bg-white/90 backdrop-blur-sm"
            >
              <div className="flex items-center gap-4">
                <div className={`w-14 h-14 rounded-2xl ${stat.gradient} flex items-center justify-center shadow-md`}>
                  <Icon name={stat.icon as any} size={28} className="text-white" />
                </div>
                <div>
                  <p className="text-sm text-muted-foreground font-medium">{stat.label}</p>
                  <p className="text-3xl font-bold mt-1">{stat.value}</p>
                </div>
              </div>
            </Card>
          ))}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2">
            <Card className="p-6 border-0 shadow-xl bg-white/90 backdrop-blur-sm">
              <Tabs value={activeSection} onValueChange={setActiveSection} className="w-full">
                <TabsList className="grid w-full grid-cols-6 mb-6 bg-purple-50/50 p-1 rounded-2xl">
                  {sections.map((section) => (
                    <TabsTrigger 
                      key={section.id} 
                      value={section.id}
                      className="rounded-xl data-[state=active]:gradient-primary data-[state=active]:text-white data-[state=active]:shadow-md transition-all"
                    >
                      <Icon name={section.icon as any} size={18} className="lg:mr-2" />
                      <span className="hidden lg:inline">{section.label}</span>
                    </TabsTrigger>
                  ))}
                </TabsList>

                <TabsContent value="chat" className="space-y-4">
                  <div className="flex items-center justify-between mb-4">
                    <h2 className="text-2xl font-bold">Активные диалоги</h2>
                    <Button className="gradient-primary shadow-md">
                      <Icon name="Plus" size={18} className="mr-2" />
                      Новый чат
                    </Button>
                  </div>
                  {recentChats.map((chat, index) => (
                    <div 
                      key={index}
                      className="p-4 rounded-2xl border border-purple-100 hover:border-purple-300 hover:shadow-md transition-all cursor-pointer bg-gradient-to-r from-white to-purple-50/30"
                    >
                      <div className="flex items-center gap-3">
                        <div className="text-3xl">{chat.avatar}</div>
                        <div className="flex-1">
                          <div className="flex items-center justify-between">
                            <h3 className="font-semibold text-lg">{chat.user}</h3>
                            <span className="text-xs text-muted-foreground">{chat.time}</span>
                          </div>
                          <p className="text-muted-foreground mt-1">{chat.message}</p>
                        </div>
                      </div>
                    </div>
                  ))}
                </TabsContent>

                <TabsContent value="generation" className="space-y-4">
                  <div className="text-center py-12">
                    <div className="w-24 h-24 mx-auto rounded-full gradient-primary flex items-center justify-center mb-6 shadow-2xl animate-pulse-soft">
                      <Icon name="Sparkles" size={48} className="text-white" />
                    </div>
                    <h2 className="text-2xl font-bold mb-3">Генерация изображений</h2>
                    <p className="text-muted-foreground mb-6 max-w-md mx-auto">
                      Создавайте уникальные изображения с помощью нейросети
                    </p>
                    <Button className="gradient-secondary shadow-lg text-lg px-8 py-6">
                      <Icon name="Wand2" size={20} className="mr-2" />
                      Начать создание
                    </Button>
                  </div>
                </TabsContent>

                <TabsContent value="editor" className="space-y-4">
                  <div className="text-center py-12">
                    <div className="w-24 h-24 mx-auto rounded-full gradient-secondary flex items-center justify-center mb-6 shadow-2xl animate-pulse-soft">
                      <Icon name="Wand2" size={48} className="text-white" />
                    </div>
                    <h2 className="text-2xl font-bold mb-3">Редактор изображений</h2>
                    <p className="text-muted-foreground mb-6 max-w-md mx-auto">
                      Редактируйте фото: удаляйте фон, меняйте цвета, добавляйте эффекты
                    </p>
                    <Button className="gradient-primary shadow-lg text-lg px-8 py-6">
                      <Icon name="Upload" size={20} className="mr-2" />
                      Загрузить фото
                    </Button>
                  </div>
                </TabsContent>

                <TabsContent value="history" className="space-y-4">
                  <h2 className="text-2xl font-bold mb-4">История операций</h2>
                  <div className="space-y-3">
                    {[1, 2, 3, 4].map((_, index) => (
                      <div key={index} className="p-4 rounded-2xl bg-gradient-to-r from-purple-50 to-blue-50 border border-purple-100">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-3">
                            <div className="w-10 h-10 rounded-xl gradient-primary flex items-center justify-center">
                              <Icon name="Image" size={20} className="text-white" />
                            </div>
                            <div>
                              <p className="font-semibold">Генерация изображения</p>
                              <p className="text-sm text-muted-foreground">5 ноября 2025, 14:23</p>
                            </div>
                          </div>
                          <Button variant="outline" size="sm" className="rounded-xl">
                            <Icon name="Eye" size={16} />
                          </Button>
                        </div>
                      </div>
                    ))}
                  </div>
                </TabsContent>

                <TabsContent value="profile" className="space-y-4">
                  <div className="text-center py-8">
                    <div className="w-32 h-32 mx-auto rounded-full gradient-primary flex items-center justify-center mb-6 shadow-2xl text-6xl">
                      🤖
                    </div>
                    <h2 className="text-3xl font-bold mb-2">AI Assistant</h2>
                    <p className="text-muted-foreground mb-6">Telegram Bot ID: 8338478306</p>
                    <div className="grid grid-cols-3 gap-4 max-w-md mx-auto">
                      <div className="p-4 rounded-2xl bg-purple-50">
                        <p className="text-2xl font-bold gradient-text">152</p>
                        <p className="text-sm text-muted-foreground">Диалога</p>
                      </div>
                      <div className="p-4 rounded-2xl bg-blue-50">
                        <p className="text-2xl font-bold gradient-text">892</p>
                        <p className="text-sm text-muted-foreground">Запроса</p>
                      </div>
                      <div className="p-4 rounded-2xl bg-pink-50">
                        <p className="text-2xl font-bold gradient-text">98%</p>
                        <p className="text-sm text-muted-foreground">Успех</p>
                      </div>
                    </div>
                  </div>
                </TabsContent>

                <TabsContent value="settings" className="space-y-4">
                  <h2 className="text-2xl font-bold mb-6">Настройки бота</h2>
                  <div className="space-y-4">
                    <Card className="p-6 border border-purple-100">
                      <div className="flex items-center justify-between">
                        <div>
                          <h3 className="font-semibold text-lg">Токен Telegram</h3>
                          <p className="text-sm text-muted-foreground">8338478306:AAFN5***</p>
                        </div>
                        <Button variant="outline" className="rounded-xl">
                          <Icon name="Copy" size={16} className="mr-2" />
                          Копировать
                        </Button>
                      </div>
                    </Card>
                    <Card className="p-6 border border-purple-100">
                      <div className="flex items-center justify-between">
                        <div>
                          <h3 className="font-semibold text-lg">Обучение под пользователя</h3>
                          <p className="text-sm text-muted-foreground">Адаптация под стиль общения</p>
                        </div>
                        <Button className="gradient-primary shadow-md">Включено</Button>
                      </div>
                    </Card>
                    <Card className="p-6 border border-purple-100">
                      <div className="flex items-center justify-between">
                        <div>
                          <h3 className="font-semibold text-lg">База данных</h3>
                          <p className="text-sm text-muted-foreground">PostgreSQL подключена</p>
                        </div>
                        <Badge className="gradient-secondary text-white">
                          <Icon name="Database" size={14} className="mr-1" />
                          Активна
                        </Badge>
                      </div>
                    </Card>
                  </div>
                </TabsContent>
              </Tabs>
            </Card>
          </div>

          <div className="space-y-6">
            <Card className="p-6 border-0 shadow-xl bg-white/90 backdrop-blur-sm">
              <h3 className="text-xl font-bold mb-4 flex items-center gap-2">
                <Icon name="Zap" size={24} className="text-purple-500" />
                Быстрые действия
              </h3>
              <div className="space-y-3">
                <Button className="w-full justify-start gradient-primary shadow-md hover:shadow-lg transition-all text-left h-auto py-4 px-6">
                  <Icon name="Send" size={20} className="mr-3" />
                  <div>
                    <p className="font-semibold">Отправить сообщение</p>
                    <p className="text-xs opacity-90">Всем пользователям</p>
                  </div>
                </Button>
                <Button className="w-full justify-start gradient-secondary shadow-md hover:shadow-lg transition-all text-left h-auto py-4 px-6">
                  <Icon name="BarChart" size={20} className="mr-3" />
                  <div>
                    <p className="font-semibold">Аналитика</p>
                    <p className="text-xs opacity-90">Статистика использования</p>
                  </div>
                </Button>
                <Button variant="outline" className="w-full justify-start border-purple-200 hover:border-purple-400 transition-all text-left h-auto py-4 px-6">
                  <Icon name="Download" size={20} className="mr-3 text-purple-500" />
                  <div>
                    <p className="font-semibold">Экспорт данных</p>
                    <p className="text-xs text-muted-foreground">Скачать историю</p>
                  </div>
                </Button>
              </div>
            </Card>

            <Card className="p-6 border-0 shadow-xl gradient-primary text-white">
              <div className="flex items-start gap-3 mb-4">
                <Icon name="Lightbulb" size={24} />
                <div>
                  <h3 className="text-lg font-bold mb-2">Совет дня</h3>
                  <p className="text-sm opacity-90">
                    Используйте персонализацию для повышения точности ответов бота. 
                    Чем больше диалогов, тем умнее становится ассистент!
                  </p>
                </div>
              </div>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Index;
