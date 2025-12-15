'use client';

import { useState } from 'react';

// 模拟数据
const mockBalances = {
  usdt: 50000,
  btc: 0.005,
};

const mockPlans = [
  {
    id: '1',
    asset: 'BTC',
    amount: 100,
    interval: '每周',
    duration: '6个月',
    nextExecution: '2024-06-20',
    status: 'active',
  },
];

function Home() {
  // 状态管理
  const [depositAmount, setDepositAmount] = useState('');
  const [withdrawAmount, setWithdrawAmount] = useState('');
  const [investmentAmount, setInvestmentAmount] = useState('');
  const [investmentInterval, setInvestmentInterval] = useState('每周');
  const [investmentDuration, setInvestmentDuration] = useState('6个月');
  const [showCreatePlanForm, setShowCreatePlanForm] = useState(false);
  const [showChatModal, setShowChatModal] = useState(false);
  const [chatMessages, setChatMessages] = useState([{ sender: '', content: '' }]);

  const [pendingPlan, setPendingPlan] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [chatInput, setChatInput] = useState('');

  // 模拟数据
  const balances = mockBalances;
  const plans = mockPlans;

  // 模拟存款操作
  const handleDeposit = () => {
    if (depositAmount && parseFloat(depositAmount) > 0) {
      console.log('存款金额:', depositAmount);
      setDepositAmount('');
    }
  };

  // 模拟提款操作
  const handleWithdraw = () => {
    if (withdrawAmount && parseFloat(withdrawAmount) > 0) {
      console.log('提款金额:', withdrawAmount);
      setWithdrawAmount('');
    }
  };

  // 模拟创建投资计划
  const handleCreatePlan = () => {
    if (investmentAmount && parseFloat(investmentAmount) > 0) {
      console.log('创建投资计划:', {
        amount: investmentAmount,
        interval: investmentInterval,
        duration: investmentDuration,
      });
      setInvestmentAmount('');
      setShowCreatePlanForm(false);
    }
  };

  // Call Agent API
  const sendChatMessage = async () => {
    if (!chatInput.trim()) return;

    // Add user message
    const newUserMessage = { sender: 'user' as const, content: chatInput };
    setChatMessages(prev => [...prev, newUserMessage]);
    setChatInput('');
    setIsLoading(true);

    try {
      // In a real app, use environment variable for API URL
      const response = await fetch('http://localhost:8000/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: newUserMessage.content }),
      });

      const data = await response.json();
      let aiContent = "";

      if (data.type === 'dca') {
        // Handle DCA intent
        // Expected format from Agent: { status: "success", data: { ... } }
        const result = data.response;
        if (result.status === 'success' && result.data) {
          const plan = result.data;
          aiContent = `I've prepared a DCA plan for you: Buy ${plan.amount} ${plan.targetToken} with ${plan.sourceToken} ${plan.frequency}. Do you want to proceed?`;
          setPendingPlan(plan);
          setShowCreatePlanForm(true); // Re-use the form or a new modal? Let's populate the form
          setInvestmentAmount(plan.amount.toString());
          setInvestmentInterval(plan.frequency);
          // setInvestmentDuration(plan.duration); // map duration if possible
        } else {
          aiContent = "I understood you want to find a DCA plan, but I couldn't get the details.";
        }
      } else if (data.type === 'mental_support') {
        aiContent = data.response.message || data.response;
      } else {
        aiContent = JSON.stringify(data.response);
      }

      setChatMessages(prev => [...prev, { sender: 'assistant', content: aiContent }]);

    } catch (error) {
      console.error(error);
      setChatMessages(prev => [...prev, { sender: 'assistant', content: "Sorry, I couldn't connect to the HODL Brain." }]);
    } finally {
      setIsLoading(false);
    }
  };

  // 简化的欢迎信息渲染
  const renderWelcomeMessage = () => {
    return (
      <div className="flex flex-col gap-4 items-center justify-center">
        <h2 className="text-2xl font-bold text-gray-800">欢迎使用韭菜罐子 (HODL Box)</h2>
        <p className="text-gray-600 mb-8">简单安全的定投服务</p>
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      {/* 导航栏 */}
      <header className="bg-white shadow-sm">
        <div className="container mx-auto px-4 py-4 flex justify-between items-center">
          <div className="flex items-center">
            <h1 className="text-2xl font-bold text-blue-600">韭菜罐子</h1>
            <span className="ml-2 text-gray-500 text-sm">HODL Box</span>
          </div>

          <div className="flex items-center gap-4">
            <button
              onClick={() => setShowChatModal(true)}
              className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
            >
              💬 心理按摩
            </button>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {/* 账户概览 */}
          <div className="md:col-span-1">
            <div className="bg-white rounded-xl shadow-md p-6">
              <h2 className="text-xl font-bold text-gray-800 mb-4">账户概览</h2>

              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">USDT 余额</span>
                  <span className="font-semibold">{balances?.usdt || 0}</span>
                </div>

                <div className="flex justify-between items-center">
                  <span className="text-gray-600">BTC 余额</span>
                  <span className="font-semibold">{balances?.btc || 0}</span>
                </div>
              </div>
            </div>

            {/* 存款/提款表单 */}
            <div className="bg-white rounded-xl shadow-md p-6 mt-6">
              <h2 className="text-xl font-bold text-gray-800 mb-4">资金管理</h2>

              {/* 存款 */}
              <div className="mb-6">
                <h3 className="text-lg font-medium text-gray-700 mb-2">存款</h3>
                <div className="flex gap-2">
                  <input
                    type="number"
                    placeholder="输入金额"
                    value={depositAmount}
                    onChange={(e) => setDepositAmount(e.target.value)}
                    className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  />
                  <button
                    onClick={handleDeposit}
                    disabled={!depositAmount}
                    className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors disabled:opacity-50"
                  >
                    存款
                  </button>
                </div>
              </div>

              {/* 提款 */}
              <div>
                <h3 className="text-lg font-medium text-gray-700 mb-2">提款</h3>
                <div className="flex gap-2">
                  <input
                    type="number"
                    placeholder="输入金额"
                    value={withdrawAmount}
                    onChange={(e) => setWithdrawAmount(e.target.value)}
                    className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  />
                  <button
                    onClick={handleWithdraw}
                    disabled={!withdrawAmount}
                    className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors disabled:opacity-50"
                  >
                    提款
                  </button>
                </div>
              </div>
            </div>
          </div>

          {/* 投资计划 */}
          <div className="md:col-span-2">
            <div className="bg-white rounded-xl shadow-md p-6">
              <div className="flex justify-between items-center mb-6">
                <h2 className="text-xl font-bold text-gray-800">投资计划</h2>
                <button
                  onClick={() => setShowCreatePlanForm(!showCreatePlanForm)}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                >
                  {showCreatePlanForm ? '取消' : '创建计划'}
                </button>
              </div>

              {/* 创建投资计划表单 */}
              {showCreatePlanForm && (
                <div className="bg-gray-50 p-6 rounded-lg mb-6">
                  <h3 className="text-lg font-medium text-gray-700 mb-4">创建定投计划</h3>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                    <div>
                      <label className="block text-gray-700 mb-1">投资金额 (USDT)</label>
                      <input
                        type="number"
                        placeholder="每次投资金额"
                        value={investmentAmount}
                        onChange={(e) => setInvestmentAmount(e.target.value)}
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      />
                    </div>

                    <div>
                      <label className="block text-gray-700 mb-1">定投周期</label>
                      <select
                        value={investmentInterval}
                        onChange={(e) => setInvestmentInterval(e.target.value)}
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      >
                        <option value="每日">每日</option>
                        <option value="每周">每周</option>
                        <option value="每两周">每两周</option>
                        <option value="每月">每月</option>
                      </select>
                    </div>

                    <div>
                      <label className="block text-gray-700 mb-1">持续时间</label>
                      <select
                        value={investmentDuration}
                        onChange={(e) => setInvestmentDuration(e.target.value)}
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      >
                        <option value="3个月">3个月</option>
                        <option value="6个月">6个月</option>
                        <option value="1年">1年</option>
                        <option value="2年">2年</option>
                        <option value="3年">3年</option>
                        <option value="长期">长期</option>
                      </select>
                    </div>

                    <div>
                      <label className="block text-gray-700 mb-1">投资资产</label>
                      <select
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      >
                        <option value="BTC">BTC</option>
                        <option value="ETH">ETH</option>
                        <option value="SOL">SOL</option>
                        <option value="BNB">BNB</option>
                      </select>
                    </div>
                  </div>

                  <button
                    onClick={handleCreatePlan}
                    disabled={!investmentAmount}
                    className="w-full px-4 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors disabled:opacity-50"
                  >
                    确认创建计划
                  </button>
                </div>
              )}

              {/* 投资计划列表 */}
              <div className="space-y-4">
                {plans && plans.length > 0 ? (
                  plans.map((plan) => (
                    <div key={plan.id} className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 transition-colors">
                      <div className="flex justify-between items-center mb-2">
                        <h3 className="font-medium text-gray-900">{plan.asset} 定投计划</h3>
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${plan.status === 'active'
                          ? 'bg-green-100 text-green-800'
                          : 'bg-gray-100 text-gray-800'
                          }`}>
                          {plan.status === 'active' ? '执行中' : '已暂停'}
                        </span>
                      </div>

                      <div className="grid grid-cols-2 md:grid-cols-4 gap-2 text-sm text-gray-600">
                        <div>
                          <span className="block text-gray-500">定投金额</span>
                          <span className="font-medium">{plan.amount} USDT</span>
                        </div>

                        <div>
                          <span className="block text-gray-500">定投周期</span>
                          <span className="font-medium">{plan.interval}</span>
                        </div>

                        <div>
                          <span className="block text-gray-500">持续时间</span>
                          <span className="font-medium">{plan.duration}</span>
                        </div>

                        <div>
                          <span className="block text-gray-500">下次执行</span>
                          <span className="font-medium">{plan.nextExecution}</span>
                        </div>
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="text-center py-8 text-gray-500">
                    <p>您还没有创建投资计划</p>
                    <p className="text-sm mt-2">点击「创建计划」开始您的定投之旅</p>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </main>

      {/* 页脚 */}
      <footer className="bg-white border-t border-gray-200 py-6 mt-12">
        <div className="container mx-auto px-4 text-center text-gray-600">
          <p>韭菜罐子 (HODL Box) - AI链上储钱罐</p>
          <p className="text-sm mt-2">Save first, HODL smarter</p>
        </div>
      </footer>

      {/* 聊天模态框 */}
      {showChatModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl shadow-xl w-full max-w-md max-h-[90vh] flex flex-col">
            <div className="flex justify-between items-center p-4 border-b">
              <h3 className="font-bold text-gray-800">心理按摩室</h3>
              <button
                onClick={() => setShowChatModal(false)}
                className="text-gray-500 hover:text-gray-700"
              >
                ✕
              </button>
            </div>

            <div className="flex-1 overflow-y-auto p-4 space-y-4">
              {chatMessages.length > 0 ? (
                chatMessages.map((msg, index) => (
                  <div
                    key={index}
                    className={`flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}
                  >
                    <div
                      className={`max-w-[80%] p-3 rounded-lg ${msg.sender === 'user'
                        ? 'bg-blue-600 text-white rounded-br-none'
                        : 'bg-gray-100 text-gray-800 rounded-bl-none'
                        }`}
                    >
                      {msg.content}
                    </div>
                  </div>
                ))
              ) : (
                <div className="text-center text-gray-500 py-8">
                  <p>有什么烦恼想聊聊吗？</p>
                  <p className="text-sm mt-2">我会尽力为您提供心理按摩</p>
                </div>
              )}
            </div>

            <div className="border-t p-4">
              <div className="flex gap-2">
                <input
                  type="text"
                  placeholder="输入您的问题或感受..."
                  value={chatInput}
                  onChange={(e) => setChatInput(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && sendChatMessage()}
                  className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
                <button
                  onClick={sendChatMessage}
                  disabled={!chatInput.trim()}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50"
                >
                  发送
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Home;
