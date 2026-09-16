package com.ziskare.ai.ui.adapter

import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.ImageView
import android.widget.TextView
import androidx.recyclerview.widget.DiffUtil
import androidx.recyclerview.widget.ListAdapter
import androidx.recyclerview.widget.RecyclerView
import com.bumptech.glide.Glide
import com.ziskare.ai.R
import com.ziskare.ai.db.entity.Message
import java.io.File

class MessageAdapter : ListAdapter<Message, RecyclerView.ViewHolder>(Diff()) {

    companion object {
        private const val USER = 0
        private const val AI = 1
        private const val IMAGE = 2
    }

    override fun getItemViewType(pos: Int) = getItem(pos).let {
        when {
            it.type == "IMAGE" -> IMAGE
            it.role == "user" -> USER
            else -> AI
        }
    }

    override fun onCreateViewHolder(parent: ViewGroup, type: Int): RecyclerView.ViewHolder {
        val inf = LayoutInflater.from(parent.context)
        return when (type) {
            USER -> UserVH(inf.inflate(R.layout.item_message_user, parent, false))
            IMAGE -> ImgVH(inf.inflate(R.layout.item_message_image, parent, false))
            else -> AiVH(inf.inflate(R.layout.item_message_ai, parent, false))
        }
    }

    override fun onBindViewHolder(holder: RecyclerView.ViewHolder, pos: Int) {
        val m = getItem(pos)
        when (holder) {
            is UserVH -> holder.bind(m)
            is AiVH   -> holder.bind(m)
            is ImgVH  -> holder.bind(m)
        }
    }

    class UserVH(v: View) : RecyclerView.ViewHolder(v) {
        private val tv: TextView = v.findViewById(R.id.tvContent)
        fun bind(m: Message) { tv.text = m.content }
    }

    class AiVH(v: View) : RecyclerView.ViewHolder(v) {
        private val tv: TextView = v.findViewById(R.id.tvContent)
        fun bind(m: Message) { tv.text = m.content }
    }

    class ImgVH(v: View) : RecyclerView.ViewHolder(v) {
        private val img: ImageView = v.findViewById(R.id.imgGenerated)
        fun bind(m: Message) {
            val src: Any = if (File(m.content).exists()) File(m.content) else m.content
            Glide.with(img).load(src).into(img)
        }
    }

    class Diff : DiffUtil.ItemCallback<Message>() {
        override fun areItemsTheSame(a: Message, b: Message) = a.id == b.id
        override fun areContentsTheSame(a: Message, b: Message) = a == b
    }
}
